from __future__ import annotations
from ..models import InvestigationResult, SocialProfile, TimelineEntry, BreachEntry


def cross_reference(result: InvestigationResult) -> InvestigationResult:
    names_found = set()
    emails_found = set(result.contact.email_addresses)
    phones_found = set(result.contact.phone_numbers)
    usernames_found = set()
    locations_found = set()

    for tool_name, tool_res in result.raw_findings.items():
        data = tool_res.result

        if tool_name == "holehe":
            for reg in data.get("registrations", []):
                result.timeline.append(TimelineEntry(
                    event=f"Email registered on {reg}",
                    source="holehe",
                ))

        if tool_name in ("sherlock", "maigret"):
            for p in data.get("profiles", []):
                url = p.get("url", "")
                if url:
                    result.digital_presence.social_media.append(SocialProfile(
                        platform=p.get("site", "unknown"),
                        profile_url=url,
                        username=p.get("username"),
                    ))
                if p.get("name"):
                    names_found.add(p["name"])

        if tool_name == "phonenumbers":
            if data.get("country"):
                locations_found.add(data["country"])
            if data.get("location"):
                locations_found.add(data["location"])
            if data.get("carrier") and data["carrier"] != "unknown":
                pass

        if tool_name == "whatsapp":
            if data.get("whatsapp_registered"):
                result.digital_presence.messaging.whatsapp = True

        if tool_name == "telegram":
            if data.get("telegram_registered"):
                result.digital_presence.messaging.telegram = True

        if tool_name == "signal":
            if data.get("signal_available"):
                result.digital_presence.messaging.signal = True

        if tool_name == "theharvester":
            for emp in data.get("employees", []):
                if emp:
                    names_found.add(emp)

        if tool_name == "emailrep":
            details = data.get("details", {})
            for prof in details.get("profiles", []):
                result.digital_presence.social_media.append(SocialProfile(
                    platform=prof, profile_url=""
                ))
            for b in data.get("breaches", []):
                result.breach_data.breaches.append(BreachEntry(service=b))
            if data.get("blacklisted"):
                result.overview.risk_flags.append("email_blacklisted")

        if tool_name == "ghunt":
            profile = data.get("profile", {})
            if profile.get("display_name"):
                names_found.add(profile["display_name"])
            if profile.get("google_id"):
                result.identity.aliases.append(f"GoogleID: {profile['google_id']}")
            if profile.get("avatar_url"):
                pass

        if tool_name == "hibp":
            for b in data.get("breaches", []):
                result.breach_data.breaches.append(BreachEntry(
                    service=b.get("name", "unknown"),
                    date=b.get("date"),
                    data_exposed=b.get("data_classes", []),
                ))
                result.timeline.append(TimelineEntry(
                    event=f"Appeared in {b.get('name', 'unknown')} breach",
                    source="HIBP",
                    date=b.get("date"),
                ))

        if tool_name == "hibp_pastes":
            for p in data.get("pastes", []):
                result.breach_data.pastebin_mentions.append({
                    "url": p.get("Source", ""),
                    "date": p.get("Date", ""),
                    "content_snippet": "",
                })

        if tool_name == "google_images":
            if data.get("total_matches", 0) > 0:
                result.overview.risk_flags.append("photo_found_on_web")

    if names_found:
        result.identity.aliases = [n for n in names_found if n not in result.identity.aliases]
        if not result.overview.primary_name:
            result.overview.primary_name = next(iter(names_found))

    if locations_found:
        result.overview.primary_location = max(locations_found, key=len)

    result.overview.matches_found = (
        len(names_found) + len(emails_found) + len(phones_found) + len(usernames_found)
    )

    return result
