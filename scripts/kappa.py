from survey.models import Similarity, Dataset, UserProfile
from django.contrib.auth.models import User
from hypertable.thriftclient import *
from hyperthrift.gen.ttypes import *
import itertools
import requests

def computeKappa(mat):
    """ Computes the Kappa value
        @param n Number of rating per subjects (number of human raters)
        @param mat Matrix[subjects][categories]
        @return The Kappa value """
    n = checkEachLineCount(mat)   # PRE : every line count must be equal to n
    N = len(mat)
    k = len(mat[0])

    if DEBUG:
        print n, "raters."
        print N, "subjects."
        print k, "categories."

    # Computing p[]
    p = [0.0] * k
    for j in xrange(k):
        p[j] = 0.0
        for i in xrange(N):
            p[j] += mat[i][j]
        p[j] /= N*n
    if DEBUG: print "p =", p

    # Computing P[]
    P = [0.0] * N
    for i in xrange(N):
        P[i] = 0.0
        for j in xrange(k):
            P[i] += mat[i][j] * mat[i][j]
        P[i] = (P[i] - n) / (n * (n - 1))
    if DEBUG: print "P =", P

    # Computing Pbar
    Pbar = sum(P) / N
    if DEBUG: print "Pbar =", Pbar

    # Computing PbarE
    PbarE = 0.0
    for pj in p:
        PbarE += pj * pj
    if DEBUG: print "PbarE =", PbarE

    kappa = (Pbar - PbarE) / (1 - PbarE)
    if DEBUG: print "kappa =", kappa

    return kappa

def checkEachLineCount(mat):
    """ Assert that each line has a constant number of ratings
        @param mat The matrix checked
        @return The number of ratings
        @throws AssertionError If lines contain different number of ratings """
    n = sum(mat[0])

    assert all(sum(line) == n for line in mat[1:]), "Line count != %d (n value)." % n
    return n

DEBUG = True

def kappa_limited(excluded_users):
    mat = []
    with open('relations.csv') as f:
        for line in f:
            sline = line.split(';')
            source_dataset = Dataset.objects.get(nick=sline[0])
            target_dataset = Dataset.objects.get(nick=sline[1])
            sim_list = []
            sim_list.extend(Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None))
            sim_list.extend(Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset).exclude(similarity=None))

            row = []
            sim_dict = {'yes': 0, 'no': 0, 'undefined': 0}
            exclude = False
            for sim in sim_list:
                if sim.userprofile_set.first().user.username in excluded_users:
                    exclude = True
                    break
                sim_dict[sim.similarity] += 1
            if not exclude:
                row.append(sim_dict['yes'])
                row.append(sim_dict['no'])
                row.append(sim_dict['undefined'])

                mat.append(row)

    kappa = computeKappa(mat)

    print kappa

def get_three():
    datasets = itertools.combinations(Dataset.objects.all(), 2)
    count = 0
    count2 = 0
    count3 = 0
    for source_dataset, target_dataset in datasets:
        sim_list = []
        sim_list.extend(Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None))
        sim_list.extend(Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset).exclude(similarity=None))

        if len(sim_list) == 3:
            if sim_list[0].similarity == sim_list[1].similarity and sim_list[1].similarity == sim_list[2].similarity and sim_list[0].similarity != None:
                # print source_dataset.title, target_dataset.title
                # print sim_list[0].similarity , sim_list[1].similarity , sim_list[2].similarity
                count += 1
            elif (sim_list[0].similarity == sim_list[1].similarity or sim_list[1].similarity == sim_list[2].similarity or sim_list[0].similarity == sim_list[2].similarity) and None not in [sim_list[0].similarity, sim_list[1].similarity, sim_list[2].similarity]:
                count2 += 1
            else:
                count3 += 1
    print count
    print count2
    print count3

def export_totally_agreement_datasets(partial):
    client = ThriftClient("helheim.deusto.es", 15867)
    ns = client.namespace_open("gs")

    column_families = {}
    column_families["links"] = ColumnFamilySpec("links")
    column_families["nickname"] = ColumnFamilySpec("nickname")
    schema = Schema(column_families = column_families)

    client.table_create(ns, "usergs", schema)

    dataset_dict = {}

    datasets = itertools.combinations(Dataset.objects.all(), 2)
    for source_dataset, target_dataset in datasets:
        if None not in [source_dataset.nick, target_dataset.nick]:
            sim_list = []
            sim_list.extend(Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None))
            sim_list.extend(Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset).exclude(similarity=None))
            if len(sim_list) == 3:
                append_link = False
                sim_value = None
		print source_dataset.nick, target_dataset.nick, sim_list[0].similarity, sim_list[1].similarity, sim_list[2].similarity
                if sim_list[0].similarity == sim_list[1].similarity and sim_list[1].similarity == sim_list[2].similarity:
                    #print sim_list[0].similarity, sim_list[1].similarity, sim_list[2].similarity
		    print 'Append!'
                    append_link = True
                    sim_value = sim_list[0].similarity
                elif partial:
                    sim_count = 0
                    if sim_list[0].similarity == sim_list[1].similarity:
                        sim_count += 1
                        sim_value = sim_list[0].similarity
                    if sim_list[0].similarity == sim_list[2].similarity:
                        sim_count += 1
                        sim_value = sim_list[0].similarity
                    if sim_list[1].similarity == sim_list[2].similarity:
                        sim_count += 1
                        sim_value = sim_list[1].similarity
                    if sim_count >= 1:
                        append_link = True
                    else:
			pass
                        #print sim_list[0].similarity, sim_list[1].similarity, sim_list[2].similarity

                if append_link:
                    if sim_value == 'yes':
                        if source_dataset.nick not in dataset_dict:
                            dataset_dict[source_dataset.nick] = {}
                            dataset_dict[source_dataset.nick]['nick'] = source_dataset.nick
                            dataset_dict[source_dataset.nick]['links'] = []
                        if target_dataset.nick not in dataset_dict[source_dataset.nick]['links']:
                            dataset_dict[source_dataset.nick]['links'].append(target_dataset.nick)

                        if target_dataset.nick not in dataset_dict:
                            dataset_dict[target_dataset.nick] = {}
                            dataset_dict[target_dataset.nick]['nick'] = target_dataset.nick
                            dataset_dict[target_dataset.nick]['links'] = []
                        if source_dataset.nick not in dataset_dict[target_dataset.nick]['links']:
                            dataset_dict[target_dataset.nick]['links'].append(source_dataset.nick)


    print dataset_dict

    cells = []
    for source_dataset in dataset_dict:
        key = Key(row = source_dataset, column_family = "nickname")
        cell = Cell(key, dataset_dict[source_dataset]['nick'])
        cells.append(cell)
        links = ''
        for target_dataset in dataset_dict[source_dataset]['links']:
            links += ',%s' % target_dataset

        key = Key(row = source_dataset, column_family = "links")
        cell = Cell(key, links)
        cells.append(cell)

    client.set_cells(ns, "usergs", cells);

    client.namespace_close(ns);


def kappa(excluded_users):
    mat = []
    datasets = itertools.combinations(Dataset.objects.all(), 2)
    for source_dataset, target_dataset in datasets:
        sim_list = []
        sim_list.extend(Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None))
        sim_list.extend(Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset).exclude(similarity=None))

        if len(sim_list) == 3:
            row = []
            sim_dict = {'yes': 0, 'no': 0, 'undefined': 0}
            exclude = False
            for sim in sim_list:
                if sim.userprofile_set.first().user.username in excluded_users:
                    exclude = True
                    break
                sim_dict[sim.similarity] += 1
            if not exclude:
                row.append(sim_dict['yes'])
                row.append(sim_dict['no'])
                row.append(sim_dict['undefined'])

                mat.append(row)

    kappa = computeKappa(mat)
    return kappa

def get_disagreement():
    user_dict = {}
    with open('relations.csv') as f:
        for line in f:
            sline = line.split(';')
            source_dataset = Dataset.objects.get(nick=sline[0])
            target_dataset = Dataset.objects.get(nick=sline[1])
            sim_list = []
            sim_list.extend(Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset).exclude(similarity=None))
            sim_list.extend(Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset).exclude(similarity=None))

            sim_dict = {'yes': 0, 'no': 0, 'undefined': 0}
            for sim in sim_list:
                sim_dict[sim.similarity] += 1
            disagreed = False
            for key in sim_dict:
                if sim_dict[key] == 2:
                    disagreed = True

            if disagreed:
                dis_value = ''
                for key in sim_dict:
                    if sim_dict[key] == 1:
                        dis_value = key
                # print sim_dict
                # print dis_value
                for sim in sim_list:
                    if sim.similarity == dis_value:
                        if sim.userprofile_set.first().user.username not in user_dict:
                            user_dict[sim.userprofile_set.first().user.username] = 0
                        user_dict[sim.userprofile_set.first().user.username] += 1

    for key in user_dict:
        user = User.objects.get(username=key)
        userprofile = UserProfile.objects.get(user=user)
        print '%s (%s)' % (key, float(user_dict[key]) / len(userprofile.rated_datasets.all()))

def list_datasets():
    for dataset in Dataset.objects.order_by('title').all():
        print dataset.title

def user_agreement():
    datasets = []
    user_dict = {}
    with open('relations.csv') as f:
        for line in f:
            sline = line.split(';')
            source_dataset = Dataset.objects.get(nick=sline[0])
            target_dataset = Dataset.objects.get(nick=sline[1])
            datasets.append((source_dataset, target_dataset))

    users = itertools.combinations(User.objects.all(), 2)
    for user1, user2 in users:
        k = cohens_kappa(user1, user2, datasets, False)
        if k != None:
            print '%s - %s (%s)' % (user1.username, user2.username, k)

def all_user_agreement(output, log=False):
    anom_dict = {}
    result_dict = {}
    csv = open(output, 'w')
    all_users = []
    all_users = [x.username.encode('utf-8') for x in User.objects.all().exclude(username='user1').exclude(username='user2') if len(x.userprofile.rated_datasets.all()) > 0]
    print all_users
    header = 'User'
    i = 0
    for item in all_users:
        anom_dict[item] = 'evaluador-%s' % i
        header += ';%s' % 'evaluador-%s' % i
        i += 1
    header += '\n'
    csv.write(header)
    users = itertools.combinations([x for x in User.objects.all().exclude(username='user1').exclude(username='user2') if len(x.userprofile.rated_datasets.all()) > 0], 2)
    datasets = []
    for source, target in itertools.permutations(Dataset.objects.all(), 2):
        datasets.append((source, target))
    for user1, user2 in users:
        if user1.username.encode('utf-8') not in result_dict:
            empty_list = []
            for item in all_users:
                empty_list.append('-1')
            result_dict[user1.username.encode('utf-8')] = empty_list
        if user2.username.encode('utf-8') not in result_dict:
            empty_list = []
            for item in all_users:
                empty_list.append('-1')
            result_dict[user2.username.encode('utf-8')] = empty_list

        k = cohens_kappa(user1, user2, datasets, log)
        if k == None:
            k = -1
        elif k < 0:
            k = 0


        #csv.write('%s;%s;%s\n' % (user1.username.encode('utf-8'), user2.username.encode('utf-8'), k))
        pos = all_users.index(user2.username.encode('utf-8'))
        result_dict[user1.username.encode('utf-8')].insert(pos, k)
        result_dict[user1.username.encode('utf-8')].pop(pos + 1)

        pos = all_users.index(user1.username.encode('utf-8'))
        result_dict[user2.username.encode('utf-8')].insert(pos, k)
        result_dict[user2.username.encode('utf-8')].pop(pos + 1)
        if k != None:
            print '%s - %s (%s)' % (user1.username, user2.username, k)
    for item in all_users:
        result_list = result_dict[item]
        line = anom_dict[item]
        for result in result_list:
            line += ';%s' % result
        line += '\n'
        csv.write(line)
    csv.close()


def cohens_kappa(user1, user2, datasets, log):

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
            if (sim1.source_dataset == sim2.source_dataset) and (sim1.target_dataset == sim2.target_dataset) and ((sim1.source_dataset, sim1.target_dataset) in datasets or (sim1.target_dataset, sim2.source_dataset) in datasets):
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

# def user_agreement():
#     user_combinations = itertools.combinations(User.objects.all(), 2)
#     result_map = {}
#     for user1, user2 in user_combinations:
#         log = False
#         c = cohens_kappa(user1, user2, log)
#         if c != None:
#             if user1 not in result_map:
#                 result_map[user1] = {}
#             result_map[user1][user2] = c

#             if user2 not in result_map:
#                 result_map[user2] = {}
#             result_map[user2][user1] = c
#     print result_map
#     for user1 in result_map:
#         accum = 0
#         for user2 in result_map[user1]:
#             accum += result_map[user1][user2]
#         avg = float(accum) / len(result_map[user1])
#         print user1.username
#         print 'Avg agreement: %s' % avg
#         print '%' * 10

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


def get_id(url):
    return url.replace('http://datahub.io/dataset/', '').replace('\n', '')



def create_dataset(sline):

    DATAHUB_API_URL = 'http://datahub.io/api/3'

    url = sline[1]
    params = {'id': get_id(url)}
    print params
    r = requests.get('%s/action/package_show' % DATAHUB_API_URL, params=params)
    json_data = r.json()
    title = ''
    description = ''
    print json_data
    if 'title' in json_data['result']:
        if json_data['result']['title'] != None:
            title = json_data['result']['title']
    if 'notes' in json_data['result']:
        if json_data['result']['notes'] != None:
            description = json_data['result']['notes']
    example_resource = ''
    for resource in json_data['result']['resources']:
        if resource['format'] == 'example/rdf+xml':
            if resource['url'] != None:
                example_resource = resource['url']
    print 'Saving %s...' % title
    dataset = Dataset()
    dataset.title = title
    dataset.description = description
    dataset.datahub_url = url
    dataset.example_resource = example_resource
    dataset.save()

    return dataset

def import_fp(fp_file_name):

    dataset_dict = {}
    i = 0
    with open('survey_datasets.csv') as survey_datasets:
        for line in survey_datasets:
            if i > 0:
                sline = line.split(',')
                dataset_dict[sline[4]] = sline
            i += 1

    #Load datasets

    with open(fp_file_name) as fp_file:
        for line in fp_file:
            sline = line.split(';')
            source_dataset_name = sline[0].replace('.g', '').replace('\n', '')
            target_dataset_name = sline[1].replace('.g', '').replace('\n', '')
            try:
                source_dataset = Dataset.objects.get(nick=source_dataset_name)
            except:
                source_dataset = create_dataset(dataset_dict[source_dataset_name])
            try:
                target_dataset = Dataset.objects.get(nick=target_dataset_name)
            except:
                target_dataset = create_dataset(dataset_dict[target_dataset_name])
            similarity_source = Similarity.objects.filter(source_dataset=source_dataset, target_dataset=target_dataset)
            similarity_target = Similarity.objects.filter(source_dataset=target_dataset, target_dataset=source_dataset)
            for i in range(3 - len(similarity_source) - len(similarity_target)):
            	print 'Creating similarity for %s - %s' % (source_dataset.nick, target_dataset.nick)
                similarity = Similarity()
                similarity.source_dataset = source_dataset
                similarity.target_dataset = target_dataset
                similarity.similarity = None
                similarity.save()
