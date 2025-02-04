from resolver import resolve

def main():
    did_btc1 = "did:btc1:k1q2ddta4gt5n7u6d3xwhdyua57t6awrk55ut82qvurfm0qnrxx5nw7vnsy65"
    did_document = resolve(did_btc1, {})
    print(did_document)

if __name__ == "__main__":
    main()