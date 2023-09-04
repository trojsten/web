# Literal names of the categories, camps and properties
SUSI_AGAT = "Agát"
SUSI_BLYSKAVICA = "Blýskavica"
SUSI_CIFERSKY_CECH = "Cíferský-cech"
SUSI_CAMP_TYPE = "Suši sústredenie"
PUZZLEHUNT_PARTICIPATIONS_KEY_NAME = "Suši účasti na šifrovačkách"


SUSI_COMPETITION_ID = 9  # The ID (pk) of Susi competition in the database.

SUSI_AGAT_MAX_COEFFICIENT = 8  # Maximum coefficient for participants in Agat.

# The no of experience points per each event
SUSI_EXP_POINTS_FOR_PUZZLEHUNT = 3
SUSI_EXP_POINTS_FOR_SUSI_CAMP = 3
SUSI_EXP_POINTS_FOR_SOLVED_TASKS = 3
SUSI_EXP_POINTS_FOR_OTHER_CAMP = 1

# The number of tasks participant has to solve to get extra experience points
SUSI_NUMBER_OF_SOLVED_TASKS_FOR_POINTS = 8

# If big hint is public, points won't be deducted for small hint regardless of
# whether it is public or not.
SUSI_POINTS_ALLOCATION = (
    9,  # How many points will be assigned for correct submit
    2,  # How many points will be deducted if small hint is public
    4,  # How many points will be deducted if big hint is public
    0,  # How many points will be assigned for wrong submit and after deadline submit
)

# The number of wrong submits needed to decrease the points received for the task by one.
# The effect stacks, e.g for 11 wrong submits the points for correct submit would be decreased by 2.
SUSI_WRONG_SUBMITS_TO_PENALTY = 5

# Maximum number of years to look behind when calculating experience points from camps
SUSI_YEARS_OF_CAMPS_HISTORY = 10
