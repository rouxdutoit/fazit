# SPDX-License-Identifier: AGPL-3.0-or-later

def header_blocks:
  reduce ($headers | splits("\r?\n")) as $line ({path: null, blocks: {}};
    if $line | test("^[ \t]*(#|!|$)") then .
    elif $line | startswith("/") then .path = ($line | sub("[ \t]+$"; ""))
    elif .path == null then error("site/_headers has a header before its path.")
    else
      .path as $path
      | ($line | capture("^[ \t]+(?<name>[^:\\s]+):[ \t]*(?<value>.*?)[ \t]*$")
         // error("site/_headers has an invalid header for \($path).")) as $field
      | .blocks[$path][$field.name | ascii_downcase] |=
        if . == null then $field.value else . + ", " + $field.value end
    end
  ) | .blocks;

def header_value($path; $name):
  .[$path][$name | ascii_downcase]
  | if . == null or . == "" then error("site/_headers is missing \($name) for \($path).") else . end;

# https://bunny.net/docs/api-reference/core/pull-zone/addupdate-edge-rule
def response_headers($path; $names):
  . as $blocks
  | [$names[] as $name | {
      ActionType: 5,
      ActionParameter1: $name,
      ActionParameter2: ($blocks | header_value($path; $name))
    }];

def rule($name; $patterns; $matching; $actions):
  $actions[0] + {
    Description: $name,
    Enabled: true,
    TriggerMatchingType: $matching,
    Triggers: [{Type: 0, PatternMatches: $patterns, PatternMatchingType: 0}],
    ExtraActions: $actions[1:]
  };

def desired_rules:
  ["/fonts/*", "/icons/*", "/images/*"] as $assets
  | [$assets[] as $path | header_value($path; "Cache-Control")] as $cache_values
  | if ($cache_values | unique | length) != 1 then
      error("site/_headers must give fonts, icons and images the same Cache-Control value.")
    else
      [
        rule("FazitSecurityHeaders"; ["*"]; 0; response_headers("/*"; [
          "Referrer-Policy",
          "X-Content-Type-Options",
          "Permissions-Policy",
          "Cross-Origin-Opener-Policy",
          "Strict-Transport-Security"
        ])),
        rule("FazitSiteCSP"; ["*/demo/*"]; 2; response_headers("/*"; ["Content-Security-Policy"])),
        rule("FazitDemoCSP"; ["*/demo/*"]; 0; response_headers("/demo/*"; ["Content-Security-Policy"])),
        rule("FazitAssetCache"; ($assets | map("*" + .)); 0;
          response_headers($assets[0]; ["Cache-Control"])),
        rule("FazitDemoLinkEn"; ["*/demo/en/"]; 0; response_headers("/demo/en/"; ["Link"])),
        rule("FazitDemoLinkDe"; ["*/demo/de/"]; 0; response_headers("/demo/de/"; ["Link"])),
        rule("FazitSecurityTxt"; ["*/.well-known/security.txt"]; 0;
          response_headers("/.well-known/security.txt"; ["Content-Type"])),
        rule("FazitWwwRedirect"; ["*://www.fazit.dev/*"]; 0; [{
          ActionType: 1, ActionParameter1: "https://fazit.dev{{path}}", ActionParameter2: "301"
        }])
      ]
    end;

def use_existing_rule($existing):
  .Description as $name
  | [$existing[] | select(.Description == $name)] as $matches
  | if ($matches | length) == 0 then .
    elif ($matches | length) > 1 then error("Bunny returned more than one rule named \($name).")
    elif ($matches[0].Guid | type != "string" or length == 0) then
      error("Bunny did not return a Guid for \($name).")
    else
      .Guid = $matches[0].Guid
      | if $matches[0].OrderIndex == null then . else .OrderIndex = $matches[0].OrderIndex end
    end;

if type != "object" or .Id != $zone_id then error("Bunny did not return pull zone \($zone_id).")
elif .EdgeRules != null and (.EdgeRules | type) != "array" then
  error("Bunny returned an invalid EdgeRules list for pull zone \($zone_id).")
else
  (.EdgeRules // []) as $existing
  | header_blocks | desired_rules
  | map(use_existing_rule($existing))[]
  | "\(.Description)\t\(tojson)"
end
