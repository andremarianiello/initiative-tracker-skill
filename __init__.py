from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_number


class InitiativeTracker(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.initiative_order = dict()

    @classmethod
    def _get_initiative(cls, message):
        initiative = message.data.get('initiative')
        return extract_number(initiative)

    @intent_file_handler('add.to.initiative.intent')
    def handle_add_character(self, message):
        character = message.data.get('character')
        initiative = self._get_initiative(message)
        self.initiative_order[character] = int(initiative)
        self.log.debug("initiative", self.initiative_order)
        self.log.debug(self.initiative_order)

        self.speak_dialog('added.to.initiative', data={
            'character': character,
            'initiative': initiative
        })

    @intent_file_handler('remove.from.initiative.intent')
    def handle_remove_character(self, message):
        character = message.data.get('character')
        del self.initiative_order[character]
        self.log.debug("initiative", self.initiative_order)

        self.speak_dialog('removed.from.initiative', data={
            'character': character
        })

    @intent_file_handler('what.is.initiative.intent')
    def handle_initiative_query(self, message):
        character = message.data.get('character')
        if character is None:
            if len(self.initiative_order) == 0:
                self.speak_dialog('empty.initiative.order')
            else:
                for character, initiative in self.initiative_order.items():
                    self.speak_dialog('character.has.initiative', data={
                        'character': character,
                        'initiative': initiative
                    })
        else:
            if character.endswith("'s"):
                character = character[:-2]
            self.speak_dialog('character.has.initiative', data={
                'character': character,
                'initiative': self.initiative_order[character]
            })


def create_skill():
    return InitiativeTracker()

