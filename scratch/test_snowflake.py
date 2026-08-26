import os
import sys
sys.path.append('src')
from inti_intelligence.snowflake_db import get_snowflake_session

session = get_snowflake_session()
print('✅ Snowflake session created')
print('Account:', session.get_current_account())
print('Warehouse:', session.get_current_warehouse())
