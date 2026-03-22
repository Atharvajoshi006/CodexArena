# accounts/management/commands/seed_hackathons.py
#
# Usage:
#   python manage.py seed_hackathons
#
# This loads all the real hackathon data from the original hackathons.html
# into the database and marks them as approved + featured (top 3).

from django.core.management.base import BaseCommand
from accounts.models import Hackathon


HACKATHONS = [
    {
        "title":             "HackwithIndia",
        "organizer":         "Devfolio",
        "org_initials":      "DV",
        "org_color":         "#3b82f6",
        "description":       "Open national hackathon for all Indian developers. Build for social impact, edtech, or health. Fully online and free to register.",
        "status":            "open",
        "location":          "online",
        "month":             3,
        "mode":              "Online",
        "tags":              "Open Theme,Social Impact,EdTech",
        "registration_link": "https://hackwithindia.devfolio.co/",
        "is_featured":       True,
        "is_approved":       True,
    },
    {
        "title":             "National Space Hackathon 2026",
        "organizer":         "IIT Delhi × ISRO",
        "org_initials":      "IIT",
        "org_color":         "#2f81f7",
        "description":       "Solve real space mission problems. Organized by IIT Delhi in association with ISRO. Present to actual space scientists.",
        "status":            "open",
        "location":          "delhi",
        "month":             3,
        "mode":              "In-Person",
        "tags":              "Space Tech,ISRO,Engineering",
        "registration_link": "https://unstop.com/hackathons/national-space-hackathon-tryst26-iit-delhi-1641554",
        "is_featured":       True,
        "is_approved":       True,
    },
    {
        "title":             "Google Solution Challenge 2026",
        "organizer":         "Google Developers",
        "org_initials":      "G",
        "org_color":         "#34a853",
        "description":       "Build for the UN Sustainable Development Goals using Google tech. Open to all GDSC members globally.",
        "status":            "open",
        "location":          "online",
        "month":             3,
        "mode":              "Online",
        "tags":              "Google,SDGs,Open Theme",
        "registration_link": "https://developers.google.com/community/gdsc-solution-challenge",
        "is_featured":       True,
        "is_approved":       True,
    },
    {
        "title":             "HaXplore — CodeFest",
        "organizer":         "IIT BHU Varanasi",
        "org_initials":      "BHU",
        "org_color":         "#58a6ff",
        "description":       "Flagship national hackathon of CodeFest by IIT (BHU). Open to all college students across 4 problem tracks.",
        "status":            "open",
        "location":          "varanasi",
        "month":             4,
        "mode":              "In-Person",
        "tags":              "General,Open Theme,National",
        "registration_link": "https://unstop.com/hackathons/haxplore-iit-varanasi-1623768",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Hacksprint 2.0",
        "organizer":         "KAHE Coimbatore",
        "org_initials":      "KA",
        "org_color":         "#f59e0b",
        "description":       "India's largest 36-hour national hackathon — 3600+ participants. Backed by Cognizant, JetBrains and Devfolio. ₹1L prize pool.",
        "status":            "upcoming",
        "location":          "coimbatore",
        "month":             4,
        "mode":              "In-Person",
        "tags":              "AI,Full Stack,IoT",
        "registration_link": "https://www.hack-sprint.tech/",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "NM-HACKS",
        "organizer":         "NMIMS Hyderabad",
        "org_initials":      "NM",
        "org_color":         "#3fb950",
        "description":       "24-hour surprise hackathon with food, stay, goodies & certificates. Solve real-world tech problems under pressure.",
        "status":            "open",
        "location":          "hyderabad",
        "month":             3,
        "mode":              "In-Person",
        "tags":              "In-Person,Surprise Theme,Student",
        "registration_link": "https://unstop.com/hackathons/nm-hacks-narsee-monjee-institute-of-management-studies-nmims-hyderabad-1629804",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Hack2Skill National Hackathon",
        "organizer":         "Hack2Skill",
        "org_initials":      "H2",
        "org_color":         "#ec4899",
        "description":       "Multi-domain online hackathon open to all students. Themes include AI, blockchain, cybersecurity and sustainability.",
        "status":            "open",
        "location":          "online",
        "month":             4,
        "mode":              "Online",
        "tags":              "AI,Blockchain,Cybersecurity",
        "registration_link": "https://hack2skill.com/hack/nationalHackathon",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Smart India Hackathon 2026",
        "organizer":         "MoE / AICTE",
        "org_initials":      "SIH",
        "org_color":         "#f85149",
        "description":       "India's biggest government-backed hackathon. Teams solve problem statements from central ministries and industry. Cash prizes worth crores.",
        "status":            "upcoming",
        "location":          "online",
        "month":             6,
        "mode":              "Hybrid",
        "tags":              "Government,National,Open Theme",
        "registration_link": "https://www.sih.gov.in/",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "FinHack 2026",
        "organizer":         "Razorpay × BITS Pilani",
        "org_initials":      "FH",
        "org_color":         "#3b82f6",
        "description":       "Fintech hackathon on payments, lending, and personal finance. Mentored by Razorpay engineers. Bengaluru-based final.",
        "status":            "upcoming",
        "location":          "bengaluru",
        "month":             5,
        "mode":              "Hybrid",
        "tags":              "FinTech,Payments,API",
        "registration_link": "https://devfolio.co/hackathons",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "HackSRM 2026",
        "organizer":         "SRM Institute",
        "org_initials":      "SR",
        "org_color":         "#8b5cf6",
        "description":       "Annual hackathon by SRM Institute of Science & Technology. Open to all domains — AI, Web3, IoT, sustainability.",
        "status":            "upcoming",
        "location":          "chennai",
        "month":             5,
        "mode":              "In-Person",
        "tags":              "AI,Web3,IoT,Sustainability",
        "registration_link": "https://hackathon.srmist.edu.in/",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "HackOdisha 4.0",
        "organizer":         "NIT Rourkela",
        "org_initials":      "NIT",
        "org_color":         "#0ea5e9",
        "description":       "36-hour online hackathon by NIT Rourkela. One of the biggest student-run hackathons in Eastern India.",
        "status":            "upcoming",
        "location":          "online",
        "month":             5,
        "mode":              "Online",
        "tags":              "Open Theme,Student,National",
        "registration_link": "https://hackodisha.tech/",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Hack This Fall 2026",
        "organizer":         "Hack This Fall",
        "org_initials":      "HF",
        "org_color":         "#f97316",
        "description":       "Virtual hackathon with a focus on social good, open source, and real-world problem solving. Prizes + mentorship.",
        "status":            "upcoming",
        "location":          "online",
        "month":             8,
        "mode":              "Online",
        "tags":              "Social Good,Open Source,Virtual",
        "registration_link": "https://hackthisfall.tech/",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Mumbai Hacks 2026",
        "organizer":         "TSEC Mumbai",
        "org_initials":      "MH",
        "org_color":         "#14b8a6",
        "description":       "Western India's largest student hackathon. 24 hours, multiple tracks, live demos to industry judges.",
        "status":            "upcoming",
        "location":          "mumbai",
        "month":             7,
        "mode":              "In-Person",
        "tags":              "AI,Web,Hardware",
        "registration_link": "https://mumbaihacks.com/",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Hackenza 2026",
        "organizer":         "IIT Madras",
        "org_initials":      "IIM",
        "org_color":         "#a855f7",
        "description":       "Build products that solve real-world problems. Open to all engineers and designers across India.",
        "status":            "closing",
        "location":          "chennai",
        "month":             3,
        "mode":              "In-Person",
        "tags":              "Product,Design,Engineering",
        "registration_link": "https://unstop.com/hackathons",
        "is_featured":       False,
        "is_approved":       True,
    },
    {
        "title":             "Hack the Mountain 4.0",
        "organizer":         "DevScript Winter of Code",
        "org_initials":      "HM",
        "org_color":         "#22d3ee",
        "description":       "Hybrid hackathon with 500+ participants. Themes: sustainability, health, education, and smart cities.",
        "status":            "upcoming",
        "location":          "online",
        "month":             6,
        "mode":              "Hybrid",
        "tags":              "Sustainability,Health,EdTech",
        "registration_link": "https://hackthemountain.tech/",
        "is_featured":       False,
        "is_approved":       True,
    },
]


class Command(BaseCommand):
    help = "Seed the database with real hackathon data from the CodexArena project."

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for data in HACKATHONS:
            obj, created = Hackathon.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {obj.title}"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"  – Skipped (already exists): {obj.title}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done! {created_count} hackathons created, {skipped_count} already existed."
        ))