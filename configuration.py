class ConfigClass:
    def __init__(self):
        self.corpusPath = 'Data'
        self.savedFileMainFolder = 'C:\\Users\\amity\\Desktop\\indexer'
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False

        print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath

    def get__corsavePath(self):
        return self.savedFileMainFolder
