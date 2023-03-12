import json
import re
import csv
import spacy
import uuid

pattern = re.compile("(identity|candidate)_?(?:id)? ?:? ?([0-9]+)", flags=re.I|re.M)
nlp = spacy.load('en_core_web_sm')

def extract_ids_from(message) -> dict:
    ids = {}
    results = pattern.findall(message)
    for match in results:
        if match[0] == "identity":
            ids["identity_id"] = match[1]
        elif match[0] == "candidate":
            ids["candidate_id"] = match[1]
    return ids


def parse_file(log_file, message_nodes, phrase_relationships, identity_relationships, candidate_relationships):
    entries = json.load(log_file)
    print(f"num entries: {len(entries)}")
    fieldnames = ["message_uuid", "module", "level", "message", "identity_id", "candidate_id", "timestamp"]
    message_nodes_writer = csv.DictWriter(message_nodes,
                                          fieldnames=fieldnames,
                                          delimiter=',',
                                          quotechar='"',
                                          quoting=csv.QUOTE_MINIMAL)
    message_nodes_writer.writeheader()

    noun_relationship_list_writer = csv.DictWriter(phrase_relationships,
                                               fieldnames=["message_uuid", "noun_phrase"],
                                               delimiter=',',
                                               quotechar='"',
                                               quoting=csv.QUOTE_MINIMAL)
    noun_relationship_list_writer.writeheader()

    identity_relationship_list_writer = csv.DictWriter(identity_relationships,
                                                       fieldnames=["message_uuid", "identity_id"],
                                                       delimiter=',',
                                                       quotechar='"',
                                                       quoting=csv.QUOTE_MINIMAL)
    identity_relationship_list_writer.writeheader()

    candidate_relationship_list_writer = csv.DictWriter(candidate_relationships,
                                                        fieldnames=["message_uuid", "candidate_id"],
                                                        delimiter=',',
                                                        quotechar='"',
                                                        quoting=csv.QUOTE_MINIMAL)
    candidate_relationship_list_writer.writeheader()

    for entry in entries:
        content = entry["@message"]
        if isinstance(content, str):
            continue
        message_uuid = str(uuid.uuid4())
        module = content.get("name")
        level = content.get("levelname")
        message = content.get("message")
        identity_id = content.get("identity_id")
        candidate_id = content.get("candidate_id")
        timestamp = content.get("timestamp")

        if not identity_id or not candidate_id:
            ids = extract_ids_from(message)
            if not identity_id:
                identity_id = ids.get("identity_id")
            if not candidate_id:
                candidate_id = ids.get("candidate_id")

        if identity_id:
            identity_relationship_list_writer.writerow({"message_uuid": message_uuid,
                                                        "identity_id": identity_id})
            
        if candidate_id:
            candidate_relationship_list_writer.writerow({"message_uuid": message_uuid,
                                                         "candidate_id": candidate_id})
        
        parsed_message = nlp(message)

        for noun_phrase in parsed_message.noun_chunks:
            noun_phrase = re.sub('\d+', 'n', str(noun_phrase)).lower()

            noun_relationship_list_writer.writerow({"message_uuid": message_uuid,
                                                    "noun_phrase": noun_phrase})

        output = {
            "message_uuid": message_uuid,
            "module": module,
            "level": level,
            "message": message,
            "identity_id": identity_id,
            "candidate_id": candidate_id,
            "timestamp": timestamp
        }

        message_nodes_writer.writerow(output)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("logFile",
                        type=argparse.FileType('r'),
                        help="(In) AWS log exported in json format")
    parser.add_argument('message_nodes',
                        type=argparse.FileType('w'),
                        help="(Out) CSV file containing message node data")
    parser.add_argument("phrase_relationships",
                        type=argparse.FileType('w'),
                        help="(Out) CSV file containing message -> noun phrase relationships")
    parser.add_argument("identity_relationships",
                        type=argparse.FileType('w'),
                        help="(Out) CSV file containing message -> identity entity relationships")
    parser.add_argument("candidate_relationships",
                        type=argparse.FileType('w'),
                        help="(Out) CSV file containing message -> candidate entity relationships")
    # parser.add_argument('relationships', type=argparse.FileType('w'))
    args = parser.parse_args()
    parse_file(args.logFile, args.message_nodes, args.phrase_relationships, args.identity_relationships, args.candidate_relationships)
    
