from survey.models import Similarity, Dataset
import itertools

def kappa():
    combinations = itertools.combinations(Dataset.objects.all(), 2)
    sum_cells = 0
    n = 3
    N = 0
    P = 0
    total_sim = {'yes': 0, 'no': 0, 'undefined': 0}
    combinations = itertools.combinations(Dataset.objects.all(), 2)
    for source_dataset, target_dataset in combinations:
        try:
            sim_list = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
            if len(sim_list) >= 3:
                N += 1
                sim_dict = {'yes': 0, 'no': 0, 'undefined': 0}
                for sim in sim_list:
                    sum_cells += 1
                    sim_dict[sim.similarity] += 1
                    total_sim[sim.similarity] += 1
                accum = 0
                for key in sim_dict:
                    accum += pow(sim_dict[key], 2)
                accum = accum - n
                pi = float(1) / (n * (n - 1)) * accum
                P += pi
        except Exception as e:
            print e
    P =  (float(1) / N) * P
    Pe = 0
    for key in total_sim:
        Pe += pow(float(total_sim[key])/sum_cells, 2)
    if Pe == 1:
        kappa_value = 1
    else:
        kappa_value = float(P - Pe) / (1 - Pe)
    return kappa_value, None