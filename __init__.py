from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_number


class InitiativeTracker(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.initiative_order = dict()

    @classmethod
    def _get_character(cls, message):
        name = message.data.get('character')
        if name is not None and name.endswith("'s"):
            name = name[:-2]
        return name

    def _get_initiative(cls, message):
        initiative = message.data.get('initiative')
        return extract_number(initiative)

    @intent_file_handler('add.to.initiative.intent')
    def handle_add_character(self, message):
        character = self._get_character(message)
        initiative = self._get_initiative(message)
        if initiative is None:
            self.speak_dialog('invalid.initiative.dialog', data={
                'character': character
            })
        else:
            self.initiative_order[character] = initiative
            self.log.debug("initiative", self.initiative_order)
            self.log.debug(self.initiative_order)

            self.speak_dialog('added.to.initiative', data={
                'character': character,
                'initiative': initiative
            })

    @intent_file_handler('remove.from.initiative.intent')
    def handle_remove_character(self, message):
        character = self._get_character(message)
        del self.initiative_order[character]
        self.log.debug("initiative", self.initiative_order)

        self.speak_dialog('removed.from.initiative', data={
            'character': character
        })

    @intent_file_handler('what.is.initiative.intent')
    def handle_initiative_query(self, message):
        character = self._get_character(message)
        if character is None:
            if len(self.initiative_order) == 0:
                self.speak_dialog('empty.initiative.order')
            else:
                for character, initiative in self.initiative_order.items():
                    self.speak_dialog('character.has.initiative', data={
                        'character': character,
                        'initiative': initiative
                    })
        elif character not in self.initiative_order:
            self.speak_dialog('unknown.character.dialog', data={
                'character': character
            })
        else:
            self.speak_dialog('character.has.initiative', data={
                'character': character,
                'initiative': self.initiative_order[character]
            })


def create_skill():
    return InitiativeTracker()
