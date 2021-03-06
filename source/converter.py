import glob
import rdflib
import os

DIR = os.path.dirname(os.path.abspath(__file__))


def simplify_uri(uri):
    return uri.replace("https://", "http://")\
            .replace("foaf:", "http://xmlns.com/foaf/0.1/")\
            .replace("dc:", "http://purl.org/dc/elements/1.1/")\
            .replace("dbpedia:", "http://dbpedia.org/ontology/")\
            .replace("geo:", "http://www.geonames.org/")\
            .replace("pleiades:", "http://pleiades.stoa.org/places/")\
            .replace("wikidata:", "http://www.wikidata.org/wiki/")\
            .replace("viaf:", "http://viaf.org/viaf/")\
            .replace("pschema:", "http://pending.schema.org/")\
            .replace("schema:", "http://schema.org/")

graph = rdflib.Graph()
graph.bind("foaf", rdflib.Namespace("http://xmlns.com/foaf/0.1/"))
graph.bind("dc", rdflib.Namespace("http://purl.org/dc/elements/1.1/"))
graph.bind("dbpedia", rdflib.Namespace("http://dbpedia.org/ontology/"))
graph.bind("geo", rdflib.Namespace("http://www.geonames.org/"))
graph.bind("pleiades", rdflib.Namespace("http://pleiades.stoa.org/places/"))
graph.bind("wikidata", rdflib.Namespace("http://www.wikidata.org/wiki/"))
graph.bind("wikidataProp", rdflib.Namespace("http://www.wikidata.org/wiki/Property:"))
graph.bind("schema", rdflib.Namespace("http://schema.org/"))
graph.bind("viaf", rdflib.Namespace("http://viaf.org/viaf/"))
graph.bind("pschema", rdflib.Namespace("http://pending.schema.org/"))
graph.bind("relationship", rdflib.Namespace("http://www.perceive.net/schemas/20021119/relationship/#"))
graph.bind("dct", rdflib.Namespace("http://purl.org/dc/terms/"))

def get_node(obj, lang=""):

    if "http" in obj or ":" in obj:
        ret = rdflib.URIRef(simplify_uri(obj))
    else:
        lang = lang.replace("\n", "").strip()
        if lang:
            ret = rdflib.Literal(obj, lang=lang)
        else:
            ret = rdflib.Literal(obj)
            
    return ret

for TSVFile in glob.glob(os.path.join(DIR, "*.tsv")):
    with open(TSVFile, 'r') as TSVio:
        for index, line in enumerate(TSVio.readlines()):
            if index > 0:
                try:
                    lang = ""
                    sub, pred, obj, *_ = tuple(line.split("\t"))
                    sub = get_node(sub)
                    obj = get_node(obj)

                    if not pred.startswith("http") and ":" not in pred:
                        pred = "http://"+pred.replace(" ", "_")

                    pred = rdflib.URIRef(simplify_uri(pred))
                    graph.add((sub, pred, obj))
                except Exception as E:
                    print("Error on line " + str(index))
                    raise E

with open(os.path.join(DIR, "..", "lod.turtle"), "w") as output:
    output.write(graph.serialize(format='turtle').decode())

with open(os.path.join(DIR, "..", "lod.xml"), "w") as output:
    output.write(graph.serialize(format='application/rdf+xml').decode())


def normalizeUri(obj):
    if isinstance(obj, rdflib.URIRef):
        return graph.namespace_manager.normalizeUri(obj)
    return obj


with open(os.path.join(DIR, "..", "lod.tsv"), "w") as output:
    output.write("Source\tLabel\tTarget\n")
    for s, p, o in graph:
        output.write("{}\t{}\t{}\n".format(
            s,
            normalizeUri(p),
            o
        ))