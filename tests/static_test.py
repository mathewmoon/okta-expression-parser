import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from okta_expression_parser.parser import ExpressionParser

if __name__ == "__main__":
    user = {"groups": ["00g1mf03t9hPrfpaO4h7"], "location": "US", "phiaccess": "true"}
    group_exp = 'isMemberOfAnyGroup("00g1mf03t9hPrfpaO4h7", "123456")'
    exp = 'isMemberOfAnyGroup("1234","5678")'
    user_exp = 'user.location == "US" AND user.userName == "SU"'
    string_exp = 'String.stringContains(user.location, "US")'
    array_exp = "Arrays.contains({0,1,2}, 0)"
    parser = ExpressionParser(
        group_ids=["00g1mf03t9hPrfpaO4h7"], user_profile=user, log_to_stdout=True
    )
    bool_exp = 'user.booltest == "true"'
    for exp in [string_exp, user_exp, group_exp, array_exp, bool_exp]:
        print(f"Parsing exp: {exp}")
        res = parser.parse(exp)
        print(res)
