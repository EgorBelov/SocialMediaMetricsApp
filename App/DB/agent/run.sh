#!/bin/bash

# shellcheck disable=SC2046
# shellcheck disable=SC2006
export `cat config` && python core/social_agent.py &> agent_errors.logs &
python -m http.server 80 --directory web &> http_errors.logs &
echo 'starting services..'
sleep 5
echo 'put data..'
python core/put_data.py
sleep 5
