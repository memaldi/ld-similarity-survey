from survey.models import Similarity, Dataset
from django.contrib.auth.models import User
import itertools

def kappa():
    combinations = itertools.combinations(Dataset.objects.all(), 2)
    sum_cells = 0
    n = 3
    N = 0
    P = 0
    pi_dict = {}
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
                pi_dict[(source_dataset, target_dataset)] = pi
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
    return kappa_value, pi_dict

def cohens_kappa(user1, user2):

    user_profile1 = user1.userprofile
    user_profile2 = user2.userprofile
    sim_user1 = user1.userprofile.rated_datasets.all()
    sim_user2 = user2.userprofile.rated_datasets.all()

    user1_yes = 0
    user2_yes = 0
    user1_no = 0
    user2_no = 0
    user1_undefined = 0
    user2_undefined = 0
    agreement = 0
    total = 0

    for sim1 in sim_user1:
        for sim2 in sim_user2:
            if (sim1.source_dataset == sim2.source_dataset) and (sim1.target_dataset == sim2.target_dataset):
                if sim1.similarity == 'yes':
                    user1_yes += 1
                elif sim1.similarity == 'no':
                    user1_no += 1
                else:
                    user1_undefined += 1

                if sim2.similarity == 'yes':
                    user2_yes += 1
                elif sim2.similarity == 'no':
                    user2_no += 1
                else:
                    user2_undefined += 1

                if sim1.similarity == sim2.similarity:
                    agreement += 1
                total += 1
    pr_a = float(agreement) / total
    pr_e = (float(user1_yes)/total * float(user2_yes)/total) + (float(user1_no/total) * float(user2_no/total)) + (float(user1_undefined/total) * float(user2_undefined/total))
    k = (pr_a - pr_e) / (1 - pr_e)
    return k
