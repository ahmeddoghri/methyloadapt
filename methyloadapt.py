import json, random

def features(seq):
    return {seq[i:i+2] for i in range(len(seq)-1)}

def train(rows):
    score = {}
    for seq, y in rows:
        for k in features(seq):
            score[k] = score.get(k, 0) + (1 if y else -1)
    return score

def predict(model, seq):
    return sum(model.get(k, 0) for k in features(seq)) >= 0

def run(seed=17):
    rng = random.Random(seed)
    def sample(species, n):
        rows=[]
        for _ in range(n):
            y=rng.random()<.5
            s=[rng.choice("AT") for _ in range(25)]
            motif=("ACG" if species<2 else "GCG") if y else "TTA"
            pos=rng.randrange(4,18); s[pos:pos+3]=motif
            rows.append(("".join(s),y))
        return rows
    source=sample(0,180)+sample(1,180)
    target_train=sample(2,6); test=sample(2,160)
    local=train(target_train); adapted=train(source+target_train*4)
    a=sum(predict(local,x)==y for x,y in test)/len(test)
    b=sum(predict(adapted,x)==y for x,y in test)/len(test)
    return {"target_only_accuracy":round(a,3),"adapted_accuracy":round(b,3),
            "accuracy_gain_pct":round(100*(b-a),1)}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
