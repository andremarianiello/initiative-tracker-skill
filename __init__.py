from mycroft import MycroftSkill, intent_file_handler


class InitiativeTracker(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('tracker.initiative.intent')
    def handle_tracker_initiative(self, message):
        character = message.data.get('character')

        self.speak_dialog('tracker.initiative', data={
            'character': character
        })


def create_skill():
    return InitiativeTracker()

