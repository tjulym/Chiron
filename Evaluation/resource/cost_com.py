GBs = 25.0
GHzs = 100.0
state = 250

request = 2

MBs = GBs/(1024 * 1000)
GHzms = GHzs / 1000

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-M", "Chiron-M", "Faastlane-P", "Chiron-P"]

workflows = ["Social Network", "Movie Reviewing", "SLApp", "SLApp-V", "FINRA-5", "FINRA-50", "FINRA-100", "FINRA-200"]

# ASF, OpenFaaS, SAND, Faastlane, Chiron, Faastlane-M, Chiron-M, Chiron-PC, Faastlane-P, Chiron-P
SN_lats =        [ 744, 72,  85,  62,  36,  75,  76,  66,   28, 26]
SN_CPUs =        [ 10,  10,  5,   5,   1,   5,   2,   2,    5,  2]


SN_CPU_costs =   [ 75,  75, 425, 310,  36, 375, 152, 132, 140, 52]
SN_Mems =        [ 337, 337, 33,  33,  30,  39,  37,  65,   67, 65]

SN_Mem_costs =   [2875, 2875, 2805, 2046, 1080, 2925, 2812, 66*65, 28*67, 26*65]


MR_lats =        [ 707, 65,  71,  53,  30,  71,  74,  54,   22, 22]

MR_CPUs =        [ 9,   9,   4,   4,   1,   4,   2,   2,    4,  2]
MR_Mems =        [ 301, 301, 30,  30,  28,  34,  34,  59,   59, 59]


MR_CPU_costs =   [ 66,  66, 284, 212,  30, 284, 148, 108,   88, 44]
MR_Mem_costs = [2465, 2465, 71*30, 53*30, 30*28, 71*34, 74*34, 54*59, 22*59, 22*59]


App7_lats =      [443,  83,  104, 104, 69,  120, 125, 115,  54, 56]

App7_CPUs =      [ 7,   7,   4,   4,   2,   4,   3,   2,    4,  2]
App7_Mems =      [165, 165,  36,  29,  28,  33,  33,  48,   48, 48]

App7_CPU_costs = [140, 140, 416, 416, 138, 480, 375, 230, 216, 112]
App7_Mem_costs = [3915, 3915, 104*36, 104*29, 69*28, 120*33, 125*33, 115*48, 54*48, 56*48]

App10_lats =     [ 889, 172, 145, 130, 122, 184, 187, 128,  94, 93]

App10_CPUs =     [ 10,  10,  5,   5,   3,   5,   3,   4,    5,  4]
App10_Mems =     [ 165, 165, 29,  28,  27,  60,  60,  47,  47,  47]

App10_CPU_costs = [174, 174, 725, 650, 366, 920, 561, 512, 470, 372]
App10_Mem_costs = [4790, 4790, 145*29, 130*28, 122*27, 184*60, 187*60, 128*47, 94*47, 93*47]

Finra_5_lats =   [ 459, 107, 119, 109,  90, 133, 133, 124,  86, 85]

Finra_5_CPUs =   [ 6,    6,   5,   5,    1,  5,   1,   1,    5,  1]
Finra_5_Mems =   [ 182, 182, 57,  57,  53,   78,  65,  79,  82, 79]

Finra_5_CPU_costs =[97, 97,  595, 545,  90, 665, 133, 124, 430, 85]
Finra_5_Mem_costs =[5244, 5244, 119*57, 109*57, 90*53, 133*78, 133*65, 124*79, 86*82, 85*79]


Finra_50_lats =  [1711, 305, 259, 245, 174, 338, 228, 244, 123, 103]

Finra_50_CPUs =  [51,   51,  50,  50,   6,  50,  6,   11,  50,  11]
                                                #59+53*5
Finra_50_Mems = [1595, 1595,  63, 63,  57,  68,  324, 335, 338, 335]

                                                        #228*6-4-8-12-16-20
Finra_50_CPU_costs=[961, 961, 12950, 12250, 1044, 16900, 1308, 2684, 6150, 1133]
Finra_50_Mem_costs=[53465, 53465, 259*63, 245*63, 174*57, 338*68, 228*59+(228*5-4-8-12-16-20)*53, 244*335, 123*338, 103*335]


Finra_100_lats = [3732, 482, 351, 338, 285, 373, 339, 483, 159, 142]
Finra_100_CPUs = [101,  101, 100, 100, 6,   100,   9,  21, 100, 21]

                            #70+76,        #73+76        #490+170
Finra_100_Mems =[3165, 3165, 146, 146, 114, 149, 477, 614, 660, 614]
                                               #61+52*8

Finra_100_CPU_costs= [1921, 1921, 351*80+199*20, 338*80+199*20, 1430, 373*80+199*20, 
339+234+239+243+240+281+233+319+318, 483*21, 159*80+110*20, 142*21]

Finra_100_Mem_costs=[106905, 106905, 351*70+199*76, 338*70+199*76, 285*114, 
373*73+199*76, 339*61+(234+239+243+240+281+233+319+318)*52, 483*614, 159*490+110*170, 142*614]


Finra_200_lats = [8530, 838, 496, 482, 414, 522, 483, 891, 231, 236]
Finra_200_CPUs = [201,  201, 200, 200, 11,  200,  14,  21, 200, 21]

                            #70+72+63  57+115   64+56*13    #490+496+273    
Finra_200_Mems =[6305, 6305, 205, 205, 172, 211, 792, 1148, 1259, 1148]
                                          #76+72+63

Finra_200_CPU_costs= [3841, 3841, 496*80+461*80+363*40, 482*80+461*80+363*40, 414*6+389*5, 
522*80+461*80+363*40, 483+376+376+379+378+376+404+391+407+370+369+427+348+433, 891*21, 231*80+164*80+129*40, 236*21]

Finra_200_Mem_costs= [213785, 213785, 496*70+461*72+363*63, 482*70+461*72+363*63, 414*57+389*115, 
522*76+461*72+363*63, 483*64+(376+376+379+378+376+404+391+407+370+369+427+348+433)*56, 891*1148, 231*490+164*496+129*273, 236*1148]

all_cpu_costs = [SN_CPU_costs, MR_CPU_costs, App7_CPU_costs, App10_CPU_costs, Finra_5_CPU_costs, Finra_50_CPU_costs, Finra_100_CPU_costs, Finra_200_CPU_costs]
all_mem_costs = [SN_Mem_costs, MR_Mem_costs, App7_Mem_costs, App10_Mem_costs, Finra_5_Mem_costs, Finra_50_Mem_costs, Finra_100_Mem_costs, Finra_200_Mem_costs]

all_costs = []

state_costs = [10, 9, 7, 10, 6, 51, 101, 201]

mpk_cons = [1, 1, 1, 1, 1, 6, 9, 14]

for i in range(len(workflows)):
    all_cpu_costs[i].pop(-3)
    all_cpu_costs[i].pop(0)

    all_mem_costs[i].pop(-3)
    all_mem_costs[i].pop(0)

    costs = []
    for j in range(len(all_cpu_costs[i])):
        costs.append(all_cpu_costs[i][j] * GHzms * 2.1 + all_mem_costs[i][j] * MBs)

    costs[0] +=  (state_costs[i] * state)

    for j in range(1, len(costs)):
        costs[j] += request

    costs[-3] += (request * (mpk_cons[i] - 1))

    if i == 6:
        costs[2] += request
        costs[4] += request
        costs[6] += request

    if i == 7:
        costs[2] += (request * 2)
        costs[4] += (request * 2)
        costs[6] += (request * 2)

    costs = [cost/(10**7) for cost in costs]

    costs = [cost*(10**6) for cost in costs]

    all_costs.append(costs)

    print(f"==={workflows[i]}===")
    for i, method in enumerate(methods):
        print(f"{method}: ${round(costs[i], 2)}")

# print(all_costs)