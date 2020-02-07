from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_number
from collections import OrderedDict


class InitiativeTracker(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self, None, None, True)
        self.reset()

    def reset(self):
        self.clear_initiative()

    def start_combat(self):
        order = self.initiative_order()
        self.log.info("initiative order when starting combat: %s", order)
        if len(order) > 0:
            self.current_combatant = order[0][0]
            self.log.info("set current combatant to %s", self.current_combatant)
            return True
        else:
            return False

    def end_combat(self):
        self.current_combatant = None

    def in_combat(self):
        return self.current_combatant is not None

    def clear_initiative(self):
        self.end_combat()
        self.initiative_mapping = OrderedDict()

    def initiative_order(self):
        return list(sorted(self.initiative_mapping.items(), key = lambda elem: -elem[1]))

    def current_initiative(self):
        self.log.info("in combat? %s", self.in_combat())
        if not self.in_combat():
            return None

        return self.initiative_mapping[self.current_combatant]

    def next_combatant(self):
        if not self.in_combat():
            return None

        order = self.initiative_order()
        position_in_order = list(map(lambda elem: elem[0], order)).index(self.current_combatant)
        next_position_in_order = (position_in_order + 1) % len(order)
        return order[next_position_in_order][0]
    
    def next_turn(self):
        self.current_combatant = self.next_combatant()
        return self.current_combatant == self.initiative_order()[0][0]

    def speak_current_combatant(self):
        self.log.info("speaking current combatant: %s, %s", self.current_combatant, self.current_initiative())
        self.speak_dialog('character.is.up', data={
            'character': self.current_combatant,
            'initiative': self.current_initiative()
        })

    @classmethod
    def _get_character(cls, message):
        name = message.data.get('character')
        if name is not None and name.endswith("'s"):
            name = name[:-2]
        return name

    @classmethod
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

    @intent_file_handler('start.combat.intent')
    def handle_start_combat(self, message):
        if self.start_combat():
            self.speak_dialog('combat.started')
            self.log.info(self.current_combatant)
            self.speak_current_combatant()
        else:
            self.speak_dialog('empty.initiative.order')

    @intent_file_handler('end.combat.intent')
    def handle_end_combat(self, message):
        self.end_combat()
        self.speak_dialog('combat.ended')

    @intent_file_handler('clear.initiative.intent')
    def handle_clear_initiative(self, message):
        self.clear_initiative()
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
            self.speak_current_combatant()

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

    @intent_file_handler('set.current.combatant.intent')
    def handle_set_current_combatant(self, message):
        character = self._get_character(message)
        if character in self.initiative_mapping:
            self.current_combatant = character
            self.speak_current_combatant()
        else:
            self.speak_dialog('unknown.character', data={
                'character': character
            })

    @intent_file_handler('next.turn.intent')
    def handle_next_turn(self, message):
        if self.in_combat():
            end_of_round = self.next_turn()
            if end_of_round:
                self.speak_dialog('end.of.round')
            self.speak_current_combatant()
        else:
            self.speak_dialog('no.character.is.up')


def create_skill():
    return InitiativeTracker()
