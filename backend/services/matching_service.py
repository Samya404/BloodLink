from extensions import db
from models.donor import DonorProfile
from models.match import DonorMatch
from models.request import BloodRequest

class MatchingService:
    """
    Service for finding matching donors for a blood request.
    IMPORTANT: This service is for logistical coordination and donor outreach only.
    It DOES NOT make medical transfusion decisions. Always follow proper medical 
    cross-matching protocols before any blood transfusion.
    """
    
    COMPATIBILITY = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }

    @staticmethod
    def find_matches(request_id):
        return MatchingService.find_matching_donors(request_id)

    @staticmethod
    def find_matching_donors(request_id):
        """Find matching donors for a given blood request."""
        req = BloodRequest.query.get(request_id)
        if not req:
            return []

        compatible_groups = MatchingService.get_compatible_blood_groups(req.blood_group)
        
        # Query potential donors
        potential_donors = DonorProfile.query.filter(
            DonorProfile.blood_group.in_(compatible_groups),
            DonorProfile.availability_status == 'AVAILABLE'
        ).all()

        matches = []
        for donor in potential_donors:
            # Check if match already exists
            existing_match = DonorMatch.query.filter_by(request_id=req.id, donor_id=donor.id).first()
            score, reasons = MatchingService.calculate_match_score(donor, req)
            if score > 0:
                if existing_match:
                    existing_match.match_score = score
                    existing_match.reasons = ", ".join(reasons)
                    match = existing_match
                else:
                    match = DonorMatch(
                        request_id=req.id,
                        donor_id=donor.id,
                        match_score=score,
                        reasons=", ".join(reasons),
                        status='PENDING'
                    )
                    db.session.add(match)
                matches.append(match)

        db.session.commit()
        # Sort by score descending
        matches.sort(key=lambda x: (x.match_score or 0), reverse=True)
        return matches

    @staticmethod
    def get_compatible_blood_groups(recipient_blood_group):
        """Return list of donor blood groups that can donate to this recipient."""
        compatible_donors = []
        for donor_bg, recipients in MatchingService.COMPATIBILITY.items():
            if recipient_blood_group in recipients:
                compatible_donors.append(donor_bg)
        return compatible_donors

    @staticmethod
    def calculate_match_score(donor, request):
        """Calculate score and return (score, reasons)."""
        score = 0
        reasons = []

        # Exact blood group match
        if donor.blood_group == request.blood_group:
            score += 40
            reasons.append("Exact blood group match")
        else:
            score += 20
            reasons.append("Compatible blood group match")

        # Same city check
        if hasattr(donor, 'city') and hasattr(request, 'city') and donor.city and request.city:
            if donor.city.lower() == request.city.lower():
                score += 30
                reasons.append("Same city")

        # Verified donor
        if getattr(donor, 'is_verified', False):
            score += 20
            reasons.append("Verified donor")

        # Availability
        if getattr(donor, 'availability_status', '') == 'AVAILABLE':
            score += 10
            reasons.append("Currently available")

        return min(score, 100), reasons
