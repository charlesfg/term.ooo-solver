from guest5word import Guesser, GuesserFactory

wg = GuesserFactory.guesser(Guesser.STRATEGY_CHARFREQ_WITH_AVOID_KNOW, 3)
