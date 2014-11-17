from survey.models import Similarity, Dataset, UserProfile
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
            sim_list = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None)
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

def kappa_limited():
    N = 0
    sum_cells = 0
    n = 3
    N = 0
    P = 0
    pi_dict = {}
    total_sim = {'yes': 0, 'no': 0, 'undefined': 0}
    with open('relations.csv') as f:
        for line in f:
            sline = line.split(';')
            source_dataset = Dataset.objects.get(nick=sline[0])
            target_dataset = Dataset.objects.get(nick=sline[1])
            sim_list = []
            sim_list.extend(Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None))
            sim_list.extend(Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset).exclude(similarity=None))
            if len(sim_list) == 3:
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
                pi_dict[(source_dataset.title, target_dataset.title)] = pi
                P += pi
        P =  (float(1) / N) * P
        Pe = 0
        for key in total_sim:
            Pe += pow(float(total_sim[key])/sum_cells, 2)
        if Pe == 1:
            kappa_value = 1
        else:
            kappa_value = float(P - Pe) / (1 - Pe)
        return kappa_value, pi_dict


def list_datasets():
    for dataset in Dataset.objects.order_by('title').all():
        print dataset.title

def cohens_kappa(user1, user2, log):

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
    if log:
        print user1.username, user2.username
    for sim1 in sim_user1:
        for sim2 in sim_user2:
            if (sim1.source_dataset == sim2.source_dataset) and (sim1.target_dataset == sim2.target_dataset):
                if log:
                    print sim1.source_dataset.title, sim1.target_dataset.title, sim1.similarity, sim2.similarity
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
    if log:
        print agreement, total, user1_yes, user2_yes, user1_no, user2_no, user1_undefined, user2_undefined
    if total > 0:
        pr_a = float(agreement) / total
        pr_e = (float(user1_yes)/total * float(user2_yes)/total) + (float(user1_no)/total * float(user2_no)/total) + (float(user1_undefined)/total * float(user2_undefined)/total)
        if log:
            print float(user1_yes)/total * float(user2_yes)/total
            print float(user1_no)/total * float(user2_no)/total
            print float(user1_undefined)/total * float(user2_undefined)/total
            print pr_a, pr_e
        if pr_e == 1 and pr_a == 1:
            return 1
        else:
            k = (pr_a - pr_e) / (1 - pr_e)
            return k

    else:
        return None

def user_agreement():
    user_combinations = itertools.combinations(User.objects.all(), 2)
    result_map = {}
    for user1, user2 in user_combinations:
        log = False
        c = cohens_kappa(user1, user2, log)
        if c != None:
            if user1 not in result_map:
                result_map[user1] = {}
            result_map[user1][user2] = c

            if user2 not in result_map:
                result_map[user2] = {}
            result_map[user2][user1] = c
    print result_map
    for user1 in result_map:
        accum = 0
        for user2 in result_map[user1]:
            accum += result_map[user1][user2]
        avg = float(accum) / len(result_map[user1])
        print user1.username
        print 'Avg agreement: %s' % avg
        print '%' * 10

def get_user_ratings(username):
    user = User.objects.filter(username=username).get()
    for similarity in user.userprofile.rated_datasets.all():
        print '%s - %s' % (similarity.source_dataset.title, similarity.target_dataset.title)
        # userprofiles = similarity.userprofile_set.all()
        # for up in userprofiles:
        #     print up.user.username
        similarities = Similarity.objects.filter(source_dataset=similarity.source_dataset, target_dataset=similarity.target_dataset).exclude(userprofile=user.userprofile).all()
        for sim in similarities:
             for userprofile in sim.userprofile_set.all():
                print userprofile.user.username
