import sys
sys.path.append('C:\\final year project\\src')

from navigation import NavigationEngine
from config.settings import Settings

ne = NavigationEngine(Settings())

# Check Dairy in landmarks
dairy_landmark = ne.landmarks.get('Dairy')
if dairy_landmark:
    print(f'Dairy landmark: x={dairy_landmark.x}, y={dairy_landmark.y}')
else:
    print('Dairy not in landmarks')

# Check Dairy in aisles
dairy_aisle = ne.aisles.get('Dairy')
if dairy_aisle:
    print(f'Dairy aisle: x={dairy_aisle["path"][0].x}, y={dairy_aisle["path"][0].y}')
else:
    print('Dairy not in aisles')

# Check Household for comparison
household_landmark = ne.landmarks.get('Household')
if household_landmark:
    print(f'Household landmark: x={household_landmark.x}, y={household_landmark.y}')

household_aisle = ne.aisles.get('Household')
if household_aisle:
    print(f'Household aisle: x={household_aisle["path"][0].x}, y={household_aisle["path"][0].y}')
