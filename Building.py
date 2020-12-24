class Building:

    def __init__(self, json, htmlButton):
        self.name = json['name']
        self.maxLevel = json['maxLevel']
        self.priority = json['priority']
        self.htmlButton = htmlButton
        buttonText = htmlButton.text
        if buttonText.lower() == 'no disponible' or buttonText.lower() == 'máx. nivel de ampliación':
            self.haveEnoughResources = False
        else:
            self.haveEnoughResources = True
            self.level = int(htmlButton.text.replace('Ampliación a ', '').replace('Construir', '0'))

    def percentToGoal(self):
        return self.priority
        #return self.level / self.maxLevel
