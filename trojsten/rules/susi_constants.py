SUSI_AGAT = "Agát"
SUSI_BLYSKAVICA = "Blýskavica"
SUSI_CIFERSKY_CECH = "Cíferský-cech"

SUSI_COMPETITION_ID = 9
SUSI_OUTDOOR_ROUND_NUMBER = 100

SUSI_AGAT_MAX_COEFFICIENT = 8
SUSI_ELIGIBLE_FOR_TASK_BOUND = (0, 8, 8, 1000, 1000, 1000, 1000, 1000)

"""
If big hint is public, points won't be deducted for small hint regardless of
whether it is public or not.
"""

SUSI_POINTS_ALLOCATION = (
    6,  # How many points will be assigned for correct submit
    2,  # How many points will be deducted if small hint is public
    4,  # How many points will be deducted if big hint is public
    0,  # How many points will be assigned for wrong submit and after deadline submit
)

# How many days before end of the round will the hints be revealed
SUSI_HINT_DAYS = (
    7,  # Small hint
    3,  # Big hint
)

SUSI_WRONG_SUBMITS_TO_PENALTY = 5

SUSI_YEARS_OF_CAMPS_HISTORY = 10

SUSI_CAMP_TYPE = "Suši sústredenie"

PUZZLEHUNT_PARTICIPATIONS_KEY_NAME = "Suši účasti na šifrovačkách"
