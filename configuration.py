class ConfigClass:
    def __init__(self, corpus_path, output_path, stemming):
        self.corpusPath = corpus_path
        self.savedFileMainFolder = output_path
        self.toStem = stemming

    def get__corpusPath(self):
        return self.corpusPath

    def get_savedFileMainFolder(self):
        return self.savedFileMainFolder

    def get_toStem(self):
        return self.toStem
