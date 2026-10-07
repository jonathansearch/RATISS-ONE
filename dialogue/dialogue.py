#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIALOGUE v1 — on lui parle, il répond (7 intents pinnés + repli honnête).
RATISS Labs · MIT.

Le cerveau entend la phrase (fenêtres de 3 → compteur R5), devine
l'intention (motifs FR/EN), répond — enraciné dans le tissu quand la
question porte sur lui (état, comptes). v1 : motifs pinnés, pas de
généralisation LLM (voir DIALOGUE.md : la route est écrite).
"""
import os
import string
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.regles import formuler, formuler_comptes, lire_etat  # noqa: E402

INTENTS = [
    ("saluer", "FR", ("bonjour", "salut", "coucou", "bonsoir")),
    ("saluer", "EN", ("hello", "hi", "hey")),
    ("identite", "FR", ("qui es tu", "ton nom", "t appelles")),
    ("identite", "EN", ("your name", "who are you")),
    ("etat", "FR", ("tu tiens quoi", "tiens quoi", "que tiens")),
    ("etat", "EN", ("what do you hold", "what you hold")),
    ("comptes", "FR", ("combien", "tu as entendu")),
    ("comptes", "EN", ("how many", "you heard")),
    ("aide", "FR", ("aide", "sais tu faire")),
    ("aide", "EN", ("help", "what can you")),
    ("aurevoir", "FR", ("au revoir", "adieu", "bientot")),
    ("aurevoir", "EN", ("bye", "goodbye")),
]

REPONSES = {
    ("saluer", "FR"): "Bonjour ! Moi c'est RATISS. Je t'écoute.",
    ("saluer", "EN"): "Hello! I am RATISS. I am listening.",
    ("identite", "FR"): ("Je suis RATISS-ONE, un tissu de neurones intriqués. "
                         "Je tiens ce que je comprends."),
    ("identite", "EN"): ("I am RATISS-ONE, a tissue of entangled neurons. "
                         "I hold what I understand."),
    ("aide", "FR"): ("Dis-moi bonjour, demande-moi qui je suis, ce que je "
                     "tiens, ou combien j'ai entendu."),
    ("aide", "EN"): ("Say hello, ask me who I am, what I hold, "
                     "or how much I heard."),
    ("aurevoir", "FR"): "Au revoir ! Le tissu garde ce qu'il a compris.",
    ("aurevoir", "EN"): "Goodbye! The tissue keeps what it understood.",
    ("inconnu", "FR"): "Je ne comprends pas encore « {x} ». Apprends-moi des mots !",
    ("inconnu", "EN"): "I do not understand « {x} » yet. Teach me words!",
}


def normaliser(texte):
    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    return " ".join(texte.lower().translate(table).split())


MARQUEURS_FR = ("tu", "quoi", "que", "je", "est", "une", "des", "le", "la",
                "les", "merci", "beaucoup", "oui", "non", "avec", "pour",
                "comme", "suis", "mon", "ton", "te", "entendu")
MARQUEURS_EN = ("you", "what", "the", "are", "how", "much", "many", "thanks",
                "lot", "hello", "hold", "heard", "sequences", "do", "does",
                "is", "a", "an")


def deviner(texte):
    """Rend (intent, langue) ou (\"inconnu\", langue devinée)."""
    net = " " + normaliser(texte) + " "
    for intent, langue, motifs in INTENTS:
        if any(" " + m + " " in net or net.strip() == m for m in motifs):
            return intent, langue
    fr = sum(1 for w in MARQUEURS_FR if " " + w + " " in net)
    en = sum(1 for w in MARQUEURS_EN if " " + w + " " in net)
    return "inconnu", ("EN" if en > fr else "FR")


def repondre(cerveau, texte):
    """Entend (compteur R5), devine, répond. Rend (intent, langue, phrase)."""
    intent, langue = deviner(texte)
    mots = normaliser(texte).split()
    for i in range(len(mots) - 2):
        cerveau.entendre_sequence(mots[i:i + 3])
    if len(mots) == 2:  # trop court pour une fenêtre : compte quand même
        cerveau.entendre_sequence(mots + ["…"])
    if len(mots) == 1:
        cerveau.entendre_sequence(mots + ["…", "…"])
    if intent == "etat":
        return intent, langue, formuler(lire_etat(cerveau), langue)
    if intent == "comptes":
        return intent, langue, formuler_comptes(lire_etat(cerveau)["ecoutes"], langue)
    if intent == "inconnu":
        court = texte.strip()[:40]
        return intent, langue, REPONSES[(intent, langue)].format(x=court)
    return intent, langue, REPONSES[(intent, langue)]
