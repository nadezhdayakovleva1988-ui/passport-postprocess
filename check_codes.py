import postprocess as pp

codes_csv = pp.load_subdivisions()
print(f"только CSV:            {len(codes_csv)} кодов")

codes_train = pp.load_subdivisions(train_labels="data/train_labels.jsonl")
print(f"CSV + train_labels:    {len(codes_train)} кодов")
print(f"добавилось:            {len(codes_train) - len(codes_csv)}")