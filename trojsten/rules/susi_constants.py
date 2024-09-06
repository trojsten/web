# Literal names of the categories, camps and properties
SUSI_AGAT = "Agát"
SUSI_BLYSKAVICA = "Blýskavica"
SUSI_CVALAJUCI = "Cválajúci"
SUSI_DIALNICA = "Diaľnica"
HIGH_SCHOOL_CATEGORIES = [SUSI_AGAT, SUSI_BLYSKAVICA, SUSI_CVALAJUCI, SUSI_DIALNICA]
SUSI_OPEN = "Zásielkovňa"
SUSI_OLD_CIFERSKY_CECH = "Cíferský-cech"
SUSI_CAMP_TYPE = "Suši sústredenie"

# The year of the competition since which there are 4 high school categories instead of only 2
YEAR_SINCE_FOUR_CATEGORIES = 5

SUSI_COMPETITION_ID = 9  # The ID (pk) of Susi competition in the database.

COEFFICIENT_LIMITS = [6, 12, 18, 10 ** 18]  # Maximum coefficient for participants in Agat.

# The no of experience points per each event
EXP_POINTS_FOR_SUSI_CAMP = 4
EXP_POINTS_FOR_GOOD_RANK = 3

# How many top people in a category results table get extra experience points
TOP_RANK_FOR_EXP = 3

# If big hint is public, points won't be deducted for small hint regardless of
# whether it is public or not.
POINTS_ALLOCATION = (
    9,  # How many points will be assigned for correct submit
    2,  # How many points will be deducted if small hint is public
    4,  # How many points will be deducted if big hint is public
    0,  # How many points will be assigned for wrong submit and after deadline submit
)

# The number of wrong submits needed to decrease the points received for the task by one.
# The effect stacks, e.g for 11 wrong submits the points for correct submit would be decreased by 2.
WRONG_SUBMITS_TO_PENALTY = 5

# Maximum number of years to look behind when calculating experience points from camps
YEARS_OF_CAMPS_HISTORY = 10
