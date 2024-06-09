'''spacy_matcher.py: 使用spaCy进行主语匹配'''

import spacy

class SpacyMatcher:
    def __init__(self):
        self.nlp = spacy.load("zh_core_web_sm")
        print("nlp model init finished ......")

    def match(self, sentence):
        doc = self.nlp(sentence)
        subject_entities = []
        for token in doc:
            if token.dep_ == "nsubj":
                subject_entities.append(token.text)

        if not subject_entities:
            for token in doc:
                if token.dep_ == "ROOT" and token.pos_ == "VERB":
                    subject_entities.append(token.text)

        # print(f"主语实体: {subject_entities}")

        return subject_entities

if __name__ == '__main__':
    matcher = SpacyMatcher()
    sentence = "该吃什么药？"
    print(f"输入句子: {sentence}")
    subject_entities = matcher.match(sentence)
    print(f"主语实体: {subject_entities}")


