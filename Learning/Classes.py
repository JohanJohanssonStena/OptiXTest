#class Mage:
#    def __init__(self, health, mana):
#        self.health = health
#        self.mana = mana
#        print('the mage class was created')
#        print(self.health)
#    def attack(self, target):
#        target.health -=10
#
#class Monster:
#    health = 40
#
#mage = Mage(100, 200)
#monster = Monster()
#print(monster.health)
#mage.attack(monster)
#print(monster.health)


#inheritance
class Human:
    def attack(self, health):
        self.health = health
    
    def attack(self):
        print('attack')


class Warrior(Human):
    def __init__(self, health, defense):
        super().__init__(health)
        self.defense = defense


class Barbarian(Human):
    def __init__(self, health, damage):
        super().__init__(health)
        self.damage = damage

warrior = Warrior(50, 5.5)
barbarian = Barbarian(100, 8.1)
warrior.attack()
barbarian.attack()
print(warrior.health)