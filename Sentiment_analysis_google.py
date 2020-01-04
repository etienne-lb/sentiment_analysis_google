import os, codecs, pickledb
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from hashlib import md5


def make_md5(s, encoding='utf-8'):
    # Creating a unique ID per line
    return md5(s.encode(encoding)).hexdigest()


def get_sentiment(client, text):
    # Getting the sentiment + magnitude from Google Natural Language API
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='fr')
    response = client.analyze_sentiment(document=document)
    sentiment = response.document_sentiment
    return {"magnitude" : sentiment.magnitude, "score": sentiment.score}


def run(filename):
    # Just setting a limit on the number of files conversation we analyze
    limit = 10
    client = language.LanguageServiceClient()
    # The database where we store what we've already got
    cache = pickledb.load("PATH_TO_DATABASE", True)
    outputfilename = os.path.join(os.path.dirname(filename), 'google-output-new2.csv')
    with codecs.open(outputfilename, "w", encoding='utf-8') as owt:
        with codecs.open(filename, 'r', encoding='utf-8') as ord:
            for i, row in enumerate(ord):
                if i >= limit:
                    break
                row = [x for x in row.strip().split(';') if x]
                if len(row) < 4:
                    for j in range(0, (4-len(row))):
                        row.append("")
                if i == 0:
                    headers = row + ['magnitude', 'score', '\n']
                    owt.write(";".join(headers))
                    continue
                id = make_md5("%s_%s" % (row[0], row[3]))

                text = row[3]
                if len(text.split()) <= 2:
                    # If the text is too short, we don't analyze it
                    print("text too short ->%s" % text)
                    row.append('nc')
                    row.append('nc')
                    row.append('\n')
                    owt.write(";".join(row))
                    continue
                # We check if we already have the data in the DB (if yes, we don't get it again)
                sentiment = cache.get(id)
                if not sentiment:
                    try:
                        # If we don't have it, we get the sentiment with Google API
                        sentiment = get_sentiment(client, text)
                        cache.set(id, sentiment)
                    except Exception as e:
                        # If error, writing er in the file
                        row.append('er')
                        row.append('er')
                        row.append('\n')
                        owt.write(";".join(row))
                        continue

                row.append(str(sentiment['magnitude']))
                row.append(str(sentiment['score']))
                row.append('\n')
                owt.write(";".join(row))


if __name__ == "__main__":
    run("PATH_TO_INPUT_FILE")