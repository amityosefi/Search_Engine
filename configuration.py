class ConfigClass:
    def __init__(self, corpus_path, savedFileMainFolder, toStem):
        self.corpusPath = corpus_path
        self.savedFileMainFolder = savedFileMainFolder
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = toStem

        print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath

    def get_savedFileMainFolder(self):
        return self.savedFileMainFolder

    def get_toStem(self):
        return self.toStem
