import pathlib
import utils
import dataset as dataset_mod

import gcn

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

import argparse

#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('cpu')

def _train(model, gs, latencies, optimizer, criterion):
    adjacency, features, stage_nodes_lists, latency = dataset_mod.prepare_tensors(gs, latencies)

    # print(adjacency)
    # print(features)
    # exit(0)

    model.train()
    optimizer.zero_grad()

    adjacency = adjacency.to(device)
    features = features.to(device)
    latency = latency.to(device)
   
    predictions = model(adjacency, features, stage_nodes_lists)

    loss = criterion(predictions, latency)
    # print("predictions", predictions)
    # print("latency", latency)
    loss.backward()
    optimizer.step()

    return loss

def _test(model, g, latency, leeways, criterion, log_file=None):
    adjacency, features, stage_nodes_lists, latency = dataset_mod.prepare_tensors([g], [latency])

    torch.set_grad_enabled(False)
    model.eval()

    adjacency = adjacency.to(device)
    features = features.to(device)
    latency = latency.to(device)
    
    predictions = model(adjacency, features, stage_nodes_lists)

    # if not model.binary_classifier:
    if log_file is not None:
        log_file.write(f'{latency.item()} {predictions.item()} {g}\n')

    # loss = criterion(predictions, latency)

    loss = abs(predictions[0][0] - latency[0][0]) / latency[0][0]
    # print(predictions[0][0], latency[0][0])

    # print(predictions)
    # print(latency)
    # print(abs(predictions[0][0] - latency[0][0]) / latency[0][0])
    # print(loss)
    # exit(0)

    torch.set_grad_enabled(True)

    # if not model.binary_classifier:
    results = []
    for l in leeways:
        results.append(utils.valid(predictions, latency, leeway=l))

    return results, loss, (latency.item(), predictions.item())


def train(training_set,
        validation_set,
        outdir,
        target_workflow_name,
        metric,
        predictor_name,
        predictor,
        epochs,
        learning_rate,
        weight_decay,
        lr_patience,
        es_patience,
        batch_size,
        shuffle,
        optim_name,
        lr_scheduler,
        exp_name=None,
        reset_last=False,
        warmup=0,
        save=True,
        augments=None):
    
    # model_module = importlib.import_module('.' + model_name, 'eagle.models')

    outdir = pathlib.Path(outdir) / metric  / predictor_name
    outdir.mkdir(parents=True, exist_ok=True)

    if reset_last:
        predictor.reset_last()
   
    optimizer = optim.AdamW(predictor.parameters(), lr=learning_rate, weight_decay=weight_decay)

    if lr_scheduler == 'plateau':
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=lr_patience, threshold=0.01, verbose=True)
    elif lr_scheduler == 'cosine':
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=0.0)
    else:
        raise ValueError(f'Unknown lr scheduler: {lr_scheduler}')

    # criterion = torch.nn.L1Loss(reduction='sum')
    criterion = torch.nn.L1Loss(reduction='mean')

    es = utils.EarlyStopping(mode='min', patience=es_patience)

    def collate_fn(batch):
        return [e[0] for e in batch], [e[1] for e in batch]

    # print(training_set)

    training_data = torch.utils.data.DataLoader(training_set, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)
    data = validation_set

    train_corrects = [0, 0, 0, 0]
    test_corrects = [0, 0, 0, 0]
    best_accuracies = [0, 0, 0, 0]
    best_epochs = [0, 0, 0, 0]
    leeways = [0.01, 0.05, 0.1, 0.2] # +-% Accuracies
    lowest_loss = None

    if warmup:
        print(f'Warming up the last layer for {warmup} epochs')
        warmup_opt = optim.AdamW(predictor.final_params(), lr=learning_rate, weight_decay=0)
        for warmup_epoch in range(warmup):
            print(f"Warmup Epoch: {warmup_epoch}")
            for g, latency in training_data:
                loss = _train(predictor, g, latency, warmup_opt, criterion)

    for epoch_no in range(epochs):
        print(f"Epoch: {epoch_no}")

        for g, latency in training_data:
            loss = _train(predictor, g, latency, optimizer, criterion)

        train_loss = 0.

        for g, latency in training_set:
            corrects, loss, _ = _test(predictor, g, latency, leeways, criterion)
            for i, c in enumerate(corrects):
                train_corrects[i] += c
            train_loss += loss

        avg_loss = train_loss / len(training_set)

        train_accuracies = [train_correct / len(training_set) for train_correct in train_corrects]
        print(f'Top +-{leeways} Accuracy of train set for epoch {epoch_no}: {train_accuracies} ')
        print(f'Average loss of training set {epoch_no}: {avg_loss}')

        val_loss = 0.
        for g, latency in validation_set:
            corrects, loss, _ = _test(predictor, g, latency, leeways, criterion)
            for i, c in enumerate(corrects):
                test_corrects[i] += c
            val_loss += loss
        avg_loss = val_loss / len(validation_set)

        current_accuracies = [test_correct / len(validation_set) for test_correct in test_corrects]
        print(f'Average loss of validation set {epoch_no}: {avg_loss}')

        for i, best_accuracy in enumerate(best_accuracies):
            if current_accuracies[i] >= best_accuracy:
                best_accuracies[i] = current_accuracies[i]
                best_epochs[i] = epoch_no

        if torch.cuda.is_available():
            val_loss = val_loss.cpu()

        if lowest_loss is None or val_loss < lowest_loss:
            lowest_loss = val_loss
            best_predictor_weight = predictor.state_dict()
            if save:
                torch.save(best_predictor_weight, outdir / (f'predictor_{target_workflow_name}.pt' if exp_name is None else f'predictor_{exp_name}.pt'))
            print(f'Lowest val_loss: {val_loss}... Predictor model saved.')

        # if not predictor.binary_classifier:
        print(f'Top +-{leeways} Accuracy of validation set for epoch {epoch_no}: {current_accuracies}')
        print(f'[best: {best_accuracies} @ epoch {best_epochs}]')

        if lr_scheduler == 'plateau':
            if epoch_no > 20:
                scheduler.step(val_loss)
        else:
            scheduler.step()

        if epoch_no > 20:
            if es.step(val_loss):
                print('Early stopping criterion is met, stop training now.')
                break

        train_corrects = [0, 0, 0, 0]
        test_corrects = [0, 0, 0, 0]

    if save:
        torch.save(best_predictor_weight, outdir / (f'predictor_{target_workflow_name}.pt' if exp_name is None else f'predictor_{exp_name}.pt'))

    print("Training finished!")
    predictor.load_state_dict(best_predictor_weight)

    # exit(0)
    return predictor

def predict(testing_data,
        outdir,
        target_workflow_name,
        metric,
        predictor_name,
        predictor,
        log=False,
        exp_name=None,
        load=False,
        iteration=None,
        explored_models=None):
    # model_module = importlib.import_module('.' + model_name, 'eagle.models')

    if load or log:
        outdir = pathlib.Path(outdir) /  metric / predictor_name
        if log:
            outdir.mkdir(parents=True, exist_ok=True)

    if load and predictor_name != 'random':
        predictor.load_state_dict(torch.load(outdir / ('predictor.pt' if exp_name is None else f'predictor_{exp_name}.pt')))
        print('Predictor imported.')

    criterion = torch.nn.L1Loss()

    test_corrects = [0, 0, 0, 0]
    leeways = [0.01, 0.05, 0.1, 0.2]

    log_file = None
    if log:
        log_filename = 'log.txt' if exp_name is None else f'log_{exp_name}.txt'
        if iteration is not None:
            log_filename = f'iter{iteration}_' + log_filename

        log_file = outdir / log_filename
        sep = False
        if log_file.exists():
            sep = True
        log_file = log_file.open('a')
        if sep:
            log_file.write('===\n')

    predicted = []
    test_loss = 0
    for g, latency in testing_data:
        corrects, loss, values = _test(predictor, g, latency, leeways, criterion)
        for i, c in enumerate(corrects):
            test_corrects[i] += c

        test_loss += loss
        predicted.append(values[1])

    current_accuracies = [test_correct / len(testing_data) for test_correct in test_corrects]
    avg_loss = test_loss / len(testing_data)

    print(f'Top +-{leeways} Accuracy of test set: {current_accuracies}')
    print(f'Average loss of test set: {avg_loss}')

    if log:
        log_file.write('---\n')
        explored_models = explored_models or []
        for p,v in explored_models:
            log_file.write(f'{p}\n')
        log_file.write('---\n')
        
        log_file.write(f'{avg_loss}\n{current_accuracies}\n')

        log_file.close()

    return predicted

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--workflow_name', type=str, default='sn', help='Name of workflow to validation. Default: sn')
    args = parser.parse_args()

    predictor_args = {
        # "num_features": 51,
        "num_features": 17,
        "num_layers": 3,
        # "num_layers": 4,
        "num_hidden": 17,
        # "num_hidden": 32,
        # "num_hidden": 128,
        "dropout_ratio": 0.2,
        "weight_init": "thomas",
        "bias_init": "thomas",
        "binary_classifier": False
    }

    predictor = gcn.GCN(**predictor_args)
    predictor = predictor.to(device)

    target_workflow_name = args.workflow_name

    print("Train for workflow: %s" % target_workflow_name)

    dataset = dataset_mod.Dataset(target_workflow_name=target_workflow_name)
    # print(len(dataset.dataset))

    # exit(0)

    augments = None

    explored_models = dataset.train_set

    num_iter = 5

    target_batch = 64
    batch_per_iter = target_batch // num_iter
    current_batch = batch_per_iter

    target_epochs = 250
    epochs_per_iter = target_epochs // num_iter
    current_epochs = epochs_per_iter

    points_per_iter = len(dataset.train_set) // num_iter
    candidates = list(dataset.dataset)

    # train_set = dataset_mod.select_random(candidates, points_per_iter)
    # validation_set = dataset_mod.select_random([d for d in candidates if d not in train_set], points_per_iter)

    train_set = dataset.train_set[:points_per_iter]
    validation_set = dataset.valid_set

    for i in range(num_iter):
        print('Iteration', i)

        if i:
            train_set.extend(dataset.train_set[points_per_iter*i:points_per_iter*(i+1)])

        print('Number of candidate points:', len(candidates))
        print('Number of training points:', len(train_set))
        print('Batch size:', current_batch)
        print('Number of epochs:', current_epochs)

        train(training_set=train_set,
            validation_set=validation_set,
            outdir="results",
            target_workflow_name=target_workflow_name,
            metric="accuracy",
            predictor_name="gcn",
            predictor=predictor,
            learning_rate=3.5e-4,
            weight_decay=5.0e-4,
            lr_patience=10,
            es_patience=35,
            shuffle=True,
            optim_name="adamw",
            lr_scheduler="cosine",
            batch_size=current_batch,
            # batch_size=target_batch,
            epochs=current_epochs,
            # epochs=target_epochs,
            exp_name=None,
            reset_last=False,
            warmup=0,
            save=True,
            augments=augments)

        current_batch += batch_per_iter
        current_epochs += epochs_per_iter
        explored_models = train_set

    predict(dataset.dataset, outdir="results", target_workflow_name=target_workflow_name, metric="accuracy", predictor_name="gcn",
                 predictor=predictor, log=False, exp_name=None, load=False, explored_models=explored_models)

