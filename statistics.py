from models import *


def learned_words(session, user_id):
    return session.query(WordSet,Word).filter(WordSet.owner_id==user_id).join(Word, Word.word_set==WordSet.id).filter(
                                      Word.train1==3,
                                      Word.train2==3,
                                      Word.train3==3,
                                      Word.train4==3).count()


def total_words(session, user_id):
    return session.query(WordSet, Word).filter(WordSet.owner_id == user_id).join(Word,Word.word_set == WordSet.id).count()


def user_statistics(session, user):
    total = total_words(session,user.id)
    learned = learned_words(session,user.id)
    return {
        "total": total,
        "learned": learned,
        "inProgress": total - learned,
        "trainingsByDays": [int(i) for i in user.trains_completed_by_days.split(',')],
        "wordsByDays": [int(i) for i in user.words_learned_by_days.split(',')]
    }