from app.validation.questionnaire_schema import get_routing_when_list
from app.validation.validator import Validator


class AnswerRoutingValidator(Validator):
    def __init__(self, answer, routing_rules, default_route):
        super(AnswerRoutingValidator, self).__init__(answer)
        self.answer = answer
        self.routing_rules = routing_rules
        self.default_route = default_route

    def validate(self):
        self.validate_default_route()
        self.validate_routing_on_answer_options()

    def validate_default_route(self):
        if self.answer["mandatory"] and not self.default_route:
            default_route_not_defined = "Default route not defined for optional question [{}]".format(
                self.answer["id"]
            )
            self.errors.append(default_route_not_defined)

    def validate_routing_on_answer_options(self):
        answer_options = self.answer.get("options", [])
        option_values = [option["value"] for option in answer_options]
        routing_when_list = get_routing_when_list(self.routing_rules)

        if answer_options:
            for when_clause in routing_when_list:
                for when in when_clause.get("when", []):
                    if (
                        when
                        and when.get("id", "") == self.answer["id"]
                        and when.get("value", "") in option_values
                    ):
                        option_values.remove(when["value"])
                    else:
                        option_values = []

            has_unrouted_options = option_values and len(option_values) != len(
                answer_options
            )

            if has_unrouted_options and not self.default_route:
                self.errors.append(
                    "Routing rule not defined for answer [{}] missing options {}".format(
                        self.answer["id"], option_values
                    )
                )
