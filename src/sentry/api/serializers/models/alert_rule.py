from __future__ import absolute_import

from collections import defaultdict

import six

from sentry.api.serializers import register, serialize, Serializer
from sentry.incidents.models import AlertRule, AlertRuleExcludedProjects, AlertRuleTrigger


@register(AlertRule)
class AlertRuleSerializer(Serializer):
    def serialize(self, obj, attrs, user):
        return {
            "id": six.text_type(obj.id),
            "name": obj.name,
            "organizationId": six.text_type(obj.organization_id),
            "status": obj.status,
            "thresholdType": obj.threshold_type,
            "dataset": obj.dataset,
            "query": obj.query,
            "aggregation": obj.aggregation,
            "aggregations": [obj.aggregation],
            "timeWindow": obj.time_window,
            "resolution": obj.resolution,
            "alertThreshold": obj.alert_threshold,
            "resolveThreshold": obj.resolve_threshold,
            "thresholdPeriod": obj.threshold_period,
            "includeAllProjects": obj.include_all_projects,
            "dateModified": obj.date_modified,
            "dateAdded": obj.date_added,
        }


class DetailedAlertRuleSerializer(AlertRuleSerializer):
    def get_attrs(self, item_list, user, **kwargs):
        alert_rule_projects = AlertRule.objects.filter(
            id__in=[item.id for item in item_list]
        ).values_list("id", "query_subscriptions__project__slug")
        alert_rules = {item.id: item for item in item_list}
        result = defaultdict(dict)
        for alert_rule_id, project_slug in alert_rule_projects:
            rule_result = result[alert_rules[alert_rule_id]].setdefault("projects", [])
            rule_result.append(project_slug)

        triggers = AlertRuleTrigger.objects.filter(alert_rule__in=item_list).order_by("label")
        serialized_triggers = serialize(list(triggers))
        for trigger, serialized in zip(triggers, serialized_triggers):
            alert_rule_triggers = result[alert_rules[trigger.alert_rule_id]].setdefault(
                "triggers", []
            )
            alert_rule_triggers.append(serialized)

        for alert_rule_id, project_slug in AlertRuleExcludedProjects.objects.filter(
            alert_rule__in=item_list
        ).values_list("alert_rule_id", "project__slug"):
            exclusions = result[alert_rules[alert_rule_id]].setdefault("excludedProjects", [])
            exclusions.append(project_slug)
        return result

    def serialize(self, obj, attrs, user):
        data = super(DetailedAlertRuleSerializer, self).serialize(obj, attrs, user)
        data["projects"] = sorted(attrs["projects"])
        data["excludedProjects"] = sorted(attrs.get("excludedProjects", []))
        data["triggers"] = attrs.get("triggers", [])
        return data
