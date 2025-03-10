#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Liens WEs -> Channels
# Liens Channels -> WEs
# Liens WEs -> WEs
# Liens Channels -> Channels
# - featured (choice of channels)               <-
# - related (algo youtube similarity)
# - recommanded (algo youtube recommandation)

import csv
import sys

import networkx as nx


def add_node(graph, node, *attrs, **kwargs):
    if not graph.has_node(node):
        graph.add_node(node, **kwargs)


def add_edge_weight(graph, node1, node2, weight=1):
    if not graph.has_node(node1):
        print >> sys.stderr, "WARNING, trying to add link from missing node", node1
        return
    if not graph.has_node(node2):
        print >> sys.stderr, "WARNING, trying to add link to missing node", node2
        return
    if not graph.has_edge(node1, node2):
        graph.add_edge(node1, node2, weight=0)
    graph[node1][node2]['weight'] += weight

def safe_int(s):
    if not s:
        return 0
    try:
        return int(s)
    except:
        return int(float(s))

if __name__ == "__main__":

    csv_WE = sys.argv[1] if len(sys.argv) > 1 else "Polarisation post élections EU.csv"
    csv_YT = sys.argv[2] if len(sys.argv) > 2 else "full_channels.csv"
    links_WE_YT = sys.argv[3] if len(sys.argv) > 3 else "links_webentities_channels.csv"
    links_YT_WE = sys.argv[4] if len(sys.argv) > 4 else "youtube-to-corpus.csv"
    links_WE_WE = sys.argv[5] if len(sys.argv) > 5 else "Polarisation post élections EU.gexf"
    links_YT_YT = sys.argv[6] if len(sys.argv) > 6 else "links_channels_featured.gexf"

    G = nx.DiGraph()

    with open(csv_WE) as f:
        for WE in csv.DictReader(f):
            for k in WE:
                WE[k] = WE[k].decode("utf-8")
            add_node(G, WE["ID"], label=WE["NAME"], url=WE["HOME PAGE"], portee=WE["Portée (TAGS)"], fondation=WE["fondation (TAGS)"], batch=WE["batch (TAGS)"], edito=WE["edito (TAGS)"], parodique=WE["Parodique (TAGS)"], origine=WE["origine (TAGS)"], digital_nativeness=WE["digital nativeness (TAGS)"], WE_type=WE["type (TAGS)"], sexe=WE["Sexe (TAGS)"], parti=WE["Parti (TAGS)"], liste=WE["Liste (TAGS)"])

    channels = {}
    with open(csv_YT) as f:
        for channel in csv.DictReader(f):
            for k in channel:
                channel[k] = channel[k].decode("utf-8")
            channels[channel["yt_channel_id"]] = True
            add_node(G, channel["yt_channel_id"], label=channel["nom_de_la_chaine"], url=channel["lien_de_la_chaine"], categorie=channel["category"], origine=channel["pays_chaine"], langue=channel["langue_chaine"], likes=safe_int(channel["likes_totaux"]), abonnes=safe_int(channel["abonnes"]), vues=safe_int(channel["vues"]), videos=safe_int(channel["videos_publiees"]), WE_type="channel YouTube")

    with open(links_WE_YT) as f:
        for l in csv.DictReader(f):
            if l["yt_channel_id"] not in channels:
                continue
            add_edge_weight(G, l["webentity_id"], l["yt_channel_id"])

    with open(links_YT_WE) as f:
        for l in csv.DictReader(f):
            if not l["webentity"]:
                continue
            add_edge_weight(G, l["channel"], l["webentity"])

    nx.write_gexf(G, "webentities_YTchannels-bipartite-links-only.gexf", encoding="utf-8")

    G2 = nx.read_gexf(links_WE_WE)
    for (source, target, weight) in G2.edges(data='count'):
        add_edge_weight(G, source, target, weight)

    G3 = nx.read_gexf(links_YT_YT)
    for (source, target) in G3.edges():
        add_edge_weight(G, source, target)

    nx.write_gexf(G, "webentities_YTchannels-all-links.gexf", encoding="utf-8")
