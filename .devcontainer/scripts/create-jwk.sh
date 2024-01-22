#!/bin/bash

HYDRA_BASE_URL=http://hydra:4445
until curl -sf -o /dev/null "${HYDRA_BASE_URL}/health/alive"; do
  printf '.'
  sleep 1
done

echo

JWK_SET_ID=hasura-jwk-set
GET_JWT_RESPONSE_CODE=$(curl -sw '%{http_code}' -o /dev/null "${HYDRA_BASE_URL}/admin/keys/${JWK_SET_ID}")
if [ "$GET_JWT_RESPONSE_CODE" -ne "200" ]; then
  echo "Failed to get ${JWK_SET_ID}. Trying to create it ... "
  CREATE_JWT_PAYLOAD=$(jq -n --arg uid "$(uuidgen)" '{alg: "RS256", use: "sig", kid: $uid}')
  CREATE_JWT_RESPONSE_CODE=$(
    curl -X POST -sw '%{http_code}' -o /dev/null \
      -d"$CREATE_JWT_PAYLOAD" "${HYDRA_BASE_URL}/admin/keys/${JWK_SET_ID}"
  )

  if [ "$CREATE_JWT_RESPONSE_CODE" -ne "201" ]; then
    echo "Failed to create ${JWK_SET_ID}. process aborts."
    echo "URL: ${HYDRA_BASE_URL}/admin/keys/${JWK_SET_ID}"
    echo "Response code: $(curl -X POST -sw '%{http_code}' \
      -o /dev/null -d"$CREATE_JWT_PAYLOAD" \
      "${HYDRA_BASE_URL}/admin/keys/${JWK_SET_ID}")"
    exit 1
  else
    echo "${JWK_SET_ID} created."
  fi
else
  echo "${JWK_SET_ID} already exists."
fi

exit 0
