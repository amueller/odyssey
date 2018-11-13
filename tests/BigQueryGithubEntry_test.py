from odyssey.core.bigquery.BigQueryGithubEntry import BigQueryGithubEntry


def BigQueryGithubEntryMock(code=None):
    _id = '20ca0f85fed03ad533611575b32a133fbbb44a76'
    repo_name = 'abhi252/GloVeGraphs'
    path = 'LINE Evaluation/evaluateLine.py'
    if code == None:
        code = """\
import os\nimport sys\nfrom subprocess import call\nfrom sklearn.cluster import KMeans\nfrom sklearn.metrics import normalized_mutual_info_score\n\ndef evaluate(filename):\n\t#read ground truth\n\tcommunities = {}\n\tdoc = open(filename, "r")\n\tfor line in doc:\n\t\ttry:\n\t\t\ta  = line.split()\n\t\t\tcommunities[float(a[0])] = float(a[1])\n\t\texcept ValueError:\n\t\t\tcontinue\n\tdoc.close()\n\tnoof_comm = len(set(communities.values()))\n\t\n\t#generate embeddings\n\tgraphfname = filename.replace("community", "network")\n\tprint "Generating embeddings for " + graphfname + "..."\n\tcall(["cp", graphfname, "tmpi.txt"])\n\tcall(["sh", "sample.sh"])\n\n\t#read and cluster embeddings\n\tprint "Clustering embeddings of " + graphfname + "..."\n\tvectors = []\n\tdoc = open("vectors.txt","r")\n\tfor line in doc:\n\t\ta = line.split()\n\t\ttmp = []\n\t\tfor l in a:\n\t\t\ttmp.append(float(l))\n\t\tvectors.append(tmp)\n\tdoc.close()\n\tdel vectors[0] #remove summary line\n\tordered = sorted(vectors, key=lambda x: x[0])\n\tfor o in ordered:\n\t\tdel o[0] #remove node id\n\tkm = KMeans(n_clusters=noof_comm).fit(ordered)\n\n\t#evaluating\n\tcomm_labels = []\n\tfor k in sorted(communities.keys()):\n\t\tcomm_labels.append(communities[k])\n\treturn normalized_mutual_info_score(comm_labels, km.labels_)\n\n\ndef main():\n\tif len(sys.argv) < 2:\n\t\tprint "Please provide directory of graphs... Exiting..."\n\t\treturn\n\top = open("../../final/GloVeGraphs/LINE Evaluation/results.txt", "a")\n\tdirname = sys.argv[1]\n\tfilenames = os.listdir(dirname)\n\tnmi = []\n\tfor filename in filenames:\n\t\tif filename.startswith("community"):\n\t\t\tnmi.append(evaluate(dirname + "/" + filename))\n\t\t\tprint nmi\n\tscore = sum(nmi)/len(nmi)\n\top.write(dirname + " " + str(score) + "\\n")\n\top.close()\n\nmain()\n"""
    return BigQueryGithubEntry(_id, code, repo_name, path)
