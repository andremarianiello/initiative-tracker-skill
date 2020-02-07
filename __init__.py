from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_number


class InitiativeTracker(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self, None, None, True)
        self.initiative_mapping = dict()
        # this is None out of combat, but set to a character name during combat
        self.current_combatant = None

    def initiative_order(self):
        return list(sorted(self.initiative_mapping.items(), key = lambda elem: -elem[1]))

    def current_initiative(self):
        if self.current_combatant is None:
            return None
        else:
            return self.initiative_mapping[self.current_combatant]

    def next_combatant(self):
        if self.current_combatant is None:
            return None

        order = self.initiative_order()
        position_in_order = order.map(lambda c, i: c).index(self.current_combatant)
        next_position_in_order = (position_in_order + 1) % len(order)
        return order[next_position_in_order][0]

    @classmethod
    def _get_character(cls, message):
        name = message.data.get('character')
        if name is not None and name.endswith("'s"):
            name = name[:-2]
        return name

    def _get_initiative(cls, message):
        initiative = message.data.get('initiative')
        return extract_number(initiative) or None

    @intent_file_handler('add.to.initiative.intent')
    def handle_add_character(self, message):
        character = self._get_character(message)
        initiative = self._get_initiative(message)
        if initiative is None:
            self.speak_dialog('invalid.initiative', data={
                'character': character
            })
        else:
            self.initiative_mapping[character] = initiative
            self.log.debug("initiative")
            self.log.debug(self.initiative_order())

            self.speak_dialog('added.to.initiative', data={
                'character': character,
                'initiative': initiative
            })

    @intent_file_handler('remove.from.initiative.intent')
    def handle_remove_character(self, message):
        character = self._get_character(message)
        del self.initiative_mapping[character]
        self.log.debug("initiative", self.initiative_mapping)

        self.speak_dialog('removed.from.initiative', data={
            'character': character
        })

    @intent_file_handler('clear.initiative.intent')
    def handle_clear_initiative(self, message):
        self.speak_dialog('initiative.cleared')

    @intent_file_handler('what.is.initiative.intent')
    def handle_initiative_query(self, message):
        character = self._get_character(message)
        if character is None:
            if len(self.initiative_mapping) == 0:
                self.speak_dialog('empty.initiative.order')
            else:
                for character, initiative in self.initiative_order():
                    self.speak_dialog('character.has.initiative', data={
                        'character': character,
                        'initiative': initiative
                    })
        elif character not in self.initiative_mapping:
            self.speak_dialog('unknown.character', data={
                'character': character
            })
        else:
            self.speak_dialog('character.has.initiative', data={
                'character': character,
                'initiative': self.initiative_mapping[character]
            })

    @intent_file_handler('who.is.up.intent')
    def handle_who_is_up(self, message):
        if self.current_combatant is None:
            self.speak_dialog('no.character.is.up')
        else:
            self.speak_dialog('character.is.up', data={
                'character': self.current_combatant,
                'initiative': self.initiative_mapping[self.current_character]
            })

    @intent_file_handler('who.is.next.intent')
    def handle_who_is_next(self, message):
        next_combatant = self.next_combatant()
        if next_combatant is None:
            self.speak_dialog('no.character.is.up')
        else:
            self.speak_dialog('character.is.next', data={
                'character': next_combatant,
                'initiative': self.initiative_mapping[next_combatant]
            })


def create_skill():
    return InitiativeTracker()
