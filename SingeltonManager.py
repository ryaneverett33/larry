# This module solely exists because of my module design
# I would love for this to be fixed


def getPersistenceModule():
    import PersistenceModule
    return PersistenceModule.PersistenceModule.getInstance(noInit=True)
