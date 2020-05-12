from app.validation.questionnaire_schema import is_contained_in_list
from app.validation.routing.when_validator import WhenValidator
from app.validation.validator import Validator


class RoutingValidator(Validator):
    def __init__(self, element, group, questionnaire_schema):
        super(RoutingValidator, self).__init__(element)
        self.group = group
        self.questionnaire_schema = questionnaire_schema

    def validate(self):
        self.validate_routing_rules_have_default(
            self.schema_element.get("routing_rules", []), self.schema_element["id"]
        )

        for rule in self.schema_element.get("routing_rules", []):
            self.validate_routing_rule_target(self.group["blocks"], "block", rule)
            self.validate_routing_rule_target(
                self.questionnaire_schema.groups, "group", rule
            )
            self.validate_routing_rule(rule)

        for skip_condition in self.schema_element.get("skip_conditions", []):
            self.validate_skip_condition(skip_condition)

    def validate_routing_rule(self, rule):
        rule = rule.get("goto")
        if "when" in rule:
            when_validator = WhenValidator(
                rule["when"], self.schema_element["id"], self.questionnaire_schema
            )
            when_validator.validate()
            self.errors += when_validator.errors

    def validate_skip_condition(self, skip_condition):
        """
        Validate skip condition is valid
        :return: list of dictionaries containing error messages, otherwise it returns an empty list
        """
        when = skip_condition.get("when")

        when_validator = WhenValidator(
            when, self.schema_element["id"], self.questionnaire_schema
        )
        when_validator.validate()
        self.errors += when_validator.errors

    def validate_routing_rule_target(self, dict_list, goto_key, rule):
        if "goto" in rule and goto_key in rule["goto"].keys():
            referenced_id = rule["goto"][goto_key]

            if not is_contained_in_list(dict_list, referenced_id):
                invalid_block_error = "Routing rule routes to invalid {} [{}]".format(
                    goto_key, referenced_id
                )
                self.add_error(invalid_block_error)

    def validate_routing_rules_have_default(self, rules, block_or_group_id):
        """
        Ensure that a set of routing rules contains a default, without a when clause.
        """

        if rules and all(("goto" in rule for rule in rules)):
            default_routing_rule_count = 0

            for rule in rules:
                rule_directive = rule.get("goto")
                if rule_directive and "when" not in rule_directive:
                    default_routing_rule_count += 1

            if not default_routing_rule_count:
                self.add_error(
                    f"The routing rules for group or block: {block_or_group_id} "
                    f"must contain a default routing rule without a when rule"
                )
            elif default_routing_rule_count > 1:
                self.add_error(
                    f"The routing rules for group or block: {block_or_group_id} "
                    f"contain multiple default routing rules. Some of them will not be used"
                )
