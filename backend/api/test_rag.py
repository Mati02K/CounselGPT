#!/usr/bin/env python3
"""
Local RAG Testing Script

Run this to test RAG functionality without the full server.

Usage:
    python test_rag.py          # Test RAG module directly (recommended)
    python test_rag.py --http   # Test via HTTP API (requires server + requests library)

Dependencies:
    pip install sentence-transformers faiss-cpu rank_bm25 nltk numpy
    pip install requests  # Only needed for --http mode
"""

import sys
import json
import re

# Test the RAG module directly (no server needed)
print("=" * 60)
print("CounselGPT RAG Local Test")
print("=" * 60)

# Sample lease document
SAMPLE_LEASE = """
Chestnut Street
Page | 1
LEASE AGREEMENT - CALIFORNIA
This Lease Agreement ("Lease" or "Agreement") is entered into by Essex Management Corporation, a California Corporation (hereinafter
"Landlord"), as agent for the owner of the Property, Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai
(singularly and collectively "Resident") for the rental of the Leased Premises on the terms and conditions set forth in this Lease. Landlord
and Resident are referred to in this Lease as "the Parties." The Parties agree that they may enter into this Lease by electronic means,
although traditional hard copies with ink signatures may be used instead at the option of the Landlord.
1. PROPERTY: Commonly known as Chestnut Street ("Property" or "Community"). The Property location and contact information is:
Address:
143 Chestnut Street, Santa Cruz, CA, 95060
Phone Number:
(831) 469-3620
Email:
chestnut@essex.com
Website:
https://www.essexapartmenthomes.com/current-resident
2. LEASED PREMISES: Landlord rents to Resident the Premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060
(“Leased Premises”, “Premises”, or “Unit”) for use as a residence and for no other purpose.
3. RESIDENT(S) AND OTHER AUTHORIZED OCCUPANTS: All occupants 18 and over must be identified in this paragraph, sign this
Lease and are jointly and severally responsible for all obligations of Resident under this Lease.
Resident:
Haardhik Mudagere Anil
Phone Number:
(831) 529-4105
Email:
haardhiknbd@gmail.com
Resident:
Abhishek Chavan
Phone Number:
(831) 529-8632
Email:
abchavan@ucsc.edu
Resident:
Shubham Sharma
Phone Number:
(831) 529-5256
Email:
sshar134@ucsc.edu
Resident:
Mathesh Thirumalai
Phone Number:
(730) 558-8158
Email:
mati02official@gmail.com
Resident: Phone Number: Email:
Resident: Phone Number: Email:
Resident: Phone Number: Email:
Authorized Occupants other than Resident: (“Authorized Occupants”).
4. TERM & DELAY IN POSSESSION:
(a) Initial Term of Lease: 10 Months, commencing on 8/25/2025 ("Commencement Date") and terminating on 6/24/2026 ("Initial
Termination Date") subject to earlier cancellation or termination as provided in this Lease or applicable law and subject to the
renewal provisions of the "HOLDING OVER" paragraph below.
(b) Resident understands that, for reasons beyond the control of the Landlord, Landlord may not be able to provide occupancy to
Resident on said Commencement Date. If, for any reason, Landlord is unable to provide occupancy to Resident by the scheduled
Commencement Date, Resident's remedy in this event shall be limited to termination of this agreement and prompt refund of any
moneys paid. Landlord shall have no liability to Resident in this event other than the responsibility to promptly refund any moneys
paid.
5. HOLDING OVER: UNLESS ANOTHER LEASE IS SIGNED BY THE PARTIES HERETO OR UNLESS WRITTEN NOTICE OF
ELECTION NOT TO RENEW IS GIVEN BY EITHER PARTY THIRTY (30) DAYS BEFORE THE EXPIRATION OF THIS LEASE,
THIS LEASE SHALL BE AUTOMATICALLY RENEWED FOR TERMS MATCHING THE SHORTER OF THE INITIAL LEASE TERM
IDENTIFIED IN PARAGRAPH 4 OR 12 MONTHS, AND SHALL NOT BECOME MONTH-TO-MONTH UNLESS THE INITIAL TERM
IS MONTH-TO-MONTH, SUBJECT TO AMENDMENT BY LANDLORD AS SET FORTH IN CALIFORNIA CIVIL CODE (“CIV.
CODE”) § 827.
6. RENT:
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 2
(a) Resident shall pay to Landlord, as rent for the Premises, monthly base rent of $4,589 (“Monthly Base Rent”). Rent shall be paid in
full, in advance, on or before the first (1st) day of each month using a method identified in this lease. All payments, including Rent
and all other charges due Landlord hereunder shall be payable to Chestnut Street. Payment may be made on-line through
Landlord’s Residential Portal located on Landlord’s website identified in Paragraph 1. Payment by cash, cashier's check, money
order, or certified check must be made at a Walk-In-Payment System (“WIPS”) location. To utilize WIPS, contact the Management
Office to receive a mobile barcode or printed payslip. Resident can find the WIPS location nearest Resident by visiting
paynearme.com/yardicashmap, and entering Resident's Zip Code. Please plan on at least three (3) business days between the
date Resident makes a payment at a WIPS location and the date it is received by Landlord. Payment may also be made by
personal check mailed to PO BOX 209437 Austin, TX 78720-9281. Payment of rent and any other charges due to Landlord is not
accepted in person on site unless Landlord directs Resident to do so in writing (for example, in a notice to pay rent or surrender
possession). If Resident makes any payment by check, it may be converted into an electronic funds transfer (EFT). The check will
be copied and the account information on it used to electronically debit Resident's account for the amount of the check. The debit
from Resident's account may occur as early as the same day as the check is received. The debit will be shown on Resident's
regular account statement. Resident’s original check will be destroyed and, a copy of it will be kept to the extent required by
applicable laws. If the EFT cannot be processed for technical reasons, Resident authorizes the copy of the check to be processed
in place of the original check. Landlord may also accept money transfers from designated third-party financial services companies.
Resident should contact Landlord to determine if Landlord will accept this method of payment and for required information should
Resident wish to utilize this option. It is Resident's responsibility to be certain that each payment is made on or before its due date.
Notwithstanding the foregoing, Landlord reserves the right to make changes at any time to the acceptable methods for payment
of rent upon no less than sixty (60) days' written notice to Resident.
(b) If Landlord serves Resident with a three (3) day notice to pay rent or surrender possession, which Landlord may do on any date
after the first (1st) day of the month, any payment tendered following service of said notice must be in the form of a cashier’s check
or certified check.
(c) Landlord shall apply any payment made by Resident to any obligation of Resident to Landlord in Landlord's sole discretion.
Landlord shall have this right notwithstanding any allocation or direction by Resident to Landlord, which allocation shall be voidable
at Landlord's sole election, regardless of whether such direction or allocation appears on the face of the form of payment or in a
separate writing.
(d) The failure to pay any amount as outlined in this Lease including, but not limited to the payment of rent, late fees, utilities, storage,
parking, pet rent, and all other amounts shall be considered a material breach of the Lease.
7. LATE CHARGE AND NSF CHARGE: Landlord and Resident agree that the actual cost to Landlord when Resident fails to pay
amounts due under this Agreement on time, or pays by a check which is subsequently dishonored by the bank, is difficult or impossible
to ascertain, but the parties agree that Landlord does, in the event of late payment or in the event of a dishonored check, incur costs,
such as additional bookkeeping and administrative expense, bank charges, lost opportunity, cost of the late payment, etc. The parties
accordingly agree that, any time the rent for any given month is paid after the fifth (5th) day of such month, Resident will in that month
as a fair estimate of Landlord's costs and not a penalty, pay to Landlord a late charge in the sum of $85. Resident acknowledges and
agrees that where Landlord does not receive payment of any amount due under the Lease due to Resident's check being dishonored,
or returned for Non-Sufficient Funds (NSF), Resident agrees to pay Landlord, as a fair estimate of Landlord's costs and not as a
penalty a charge of $25.00 for the first dishonored check and $35.00 for any subsequent dishonored check. Both parties agree that
the payment of these sums does not constitute an agreement Resident may pay rent, or any other amount due under the Lease, late
or by dishonored check. Rent and any other amount due under the lease remains due on the first (1st) day of the month, unless
otherwise stated in this Agreement.
8. SECURITY DEPOSIT: Resident shall pay to Landlord, as security, the sum of the security deposit of $600 ("Security Deposit").
Landlord may, but shall not be obligated to, apply all or part of any Security Deposit to any of Resident's obligations hereunder.
Application of the Security Deposit to any obligation is in addition to any other remedies available to Landlord as a result of Resident's
breach of this Lease and doing so will not deprive Landlord from the right to terminate the tenancy for such breach. Resident agrees
to restore the Security Deposit to its full amount within ten (10) days of written demand by Landlord. Failure to do so is a material
breach of this Lease.
At the termination of Resident's tenancy, the Security Deposit shall be applied and accounted for in accordance with the provisions
of Civ. Code § 1950.5 and any other applicable statutes. Resident acknowledges and agrees that:
(a) After Resident has moved from and cleaned the Premises to the same level of cleanliness that existed at the time of Resident's
initial occupancy, as disclosed by the Move-In Inspection Report incorporated herein by reference, Landlord will determine whether
Resident is eligible for a refund of any or all of the Security Deposit;
(b) The amount of the refund will be determined in accordance with the following conditions and procedures:
(i) After the Resident has moved from the Premises, Landlord will inspect the Premises;
(ii) Landlord will refund to Resident the amount of the Security Deposit less any amount needed to pay the cost of the following:
a. Damages that are not due to ordinary wear and tear and are not listed on the Move-In Inspection Report (see Cleaning
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 3
Guidelines in Community Handbook);
b. Charges for late payment of rent and returned checks; and
c. Unpaid amounts owing to Landlord, including, but not limited to, monthly base rent, unpaid utility bills and any related
administrative costs, charges for unreturned keys and access devices, amounts outstanding under any other
agreements between Landlord and Resident which contemplate use of the Security Deposit in the event of a default.
(c) Resident may not use any portion of the Security Deposit toward the last month's rent.
(d) Landlord's right to possession of the Premises for Resident's default shall not be in any manner limited because Landlord holds or
applies the Security Deposit, or any portion thereof;
(e) Subject to applicable law, Landlord shall not be obligated to pay Resident interest in connection with the Security Deposit.
(f) The Security Deposit is applicable to all Residents jointly, and need not be accounted for until the permissible statutory period
after such time as all Residents have vacated the Premises, which requires the return of possession of the Premises to Landlord,
return of the keys and provision of Resident's new address to the Landlord. If Landlord does not have the Resident's forwarding
address, the Security Deposit will be sent to the Resident's last known address.
(g) Any refund due will be made payable jointly to all Residents and it shall be the responsibility of all Residents to work out between
themselves the manner of dividing the Security Deposit.
(h) If the Security Deposit is later increased by agreement of the Parties for any reason, the additional Security Deposit will be
disbursed by Landlord in accordance with this paragraph at the end of the statutory period following the end of the Resident's
tenancy. Removal of cause for the increase in the deposit, will not be grounds for early disbursement of the Security Deposit.
9. PERMITTED OCCUPANTS:
(a) The Premises shall be occupied only by the Resident(s) and the Authorized Occupants set forth in Paragraph 3. Any person who
is not listed in Paragraph 3 is a "Guest." A Guest may not stay at the Premises for more than seven (7) consecutive days, or a
total of fourteen (14) days in a 12-month period, without written permission from Landlord. Guests who stay longer than these
limits are considered unauthorized occupants, and their continued occupancy is a material breach of the Lease. Resident is
responsible for ensuring that any person who becomes an adult occupant of the Premises (after the commencement of the Lease
term) reviews the terms and conditions of the Lease, including the Proposition 65 Warning in Paragraph 20, and works with
Landlord to be added to Paragraph 3. Resident is responsible for any violation of this Lease by Resident's Guest(s). No other
persons have permission to occupy the Premises unless such permission is in writing and signed by Landlord or its authorized
agent.
(b) The acceptance of rent from any other individual shall be deemed to be the payment of rent on behalf of the Resident named in
Paragraph 3, and shall not constitute permission for the person making the payment to occupy the Premises.
(c) Should any person not named above in Paragraph 3 make any claim to right of possession of the Premises, such person shall
be deemed the guest or invitee of the named Resident and, at Landlord's sole option, their claim to right of possession may be
denied.
(d) The Authorized Occupants identified in Paragraph 3 shall be deemed to occupy the Premises under the named Resident who
are signatory to this Lease and shall thus be deemed the invitee of said named Resident. Accordingly, should any such individual
not be named in any unlawful detainer action to regain possession of the Premises, and should any such individual thereafter
make a claim to right of possession of the Premises, that claim shall be denied on the basis that said individual is the invitee of
the named Resident and does not have an independent claim to right of possession of the Premises.
(e) Resident understands that the number of occupants cannot exceed Landlord's occupancy standards for the floorplan of the
Premises, which generally is no more than two persons per bedroom plus one additional person. If the household composition
changes such that the number of occupants exceeds this occupancy standard, Resident agrees that such over-utilization shall
be grounds for Landlord to terminate this Agreement, solely at Landlord's option.
10. UTILITIES: Resident is responsible for utilities as set forth in the Utilities Addendum attached to this Lease.
11. JOINT AND SEVERAL LIABILITY AND AUTHORITY: All persons signing this Lease as Resident shall be jointly and severally liable
for all obligations under this Lease, whether or not they remain in actual possession of the Premises. The giving by any individual
Resident of a notice of termination of tenancy shall not terminate the Lease as to that Resident unless all Residents vacate the
Premises by the agreed date. Landlord may, however, treat any such notice as a notice binding against all Residents of the Premises,
and may institute unlawful detainer proceedings against all Residents in the event that they do not restore possession of the Premises
to Landlord on or before the end of the notice period. Conversely, Landlord may, at its sole option, in the event that one or more
Resident gives notice but all Residents do not return possession of the Premises to Landlord within the notice period, continue the
tenancy in effect and, if Landlord does so, all Residents, including the Resident giving notice, shall remain fully liable for all obligations
arising under this Lease whether or not they remain in occupancy of the Premises.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 4
12. NOTICES AND AUTHORIZED MANAGER:
(a) Any notice which Landlord gives to Resident shall be deemed properly served (whether or not actually received by Resident) if
served in the manner prescribed in Code of Civil Procedure (“Civ. Proc.”) § 1162. If Landlord fails to serve the notice in
accordance with the provisions of Civ. Proc. § 1162, but Resident actually receives the notice, the actual receipt shall be deemed
to cure any defects in the manner of service and the notice shall be deemed properly and personally served. Service upon any
Resident of the Premises shall be deemed valid service upon all Residents. It is not necessary to individually serve each Resident.
(b) Resident is hereby notified that Essex Management Corporation is authorized to manage the property on the Owner's behalf and
to accept service of process, notices or demands on behalf of the Landlord. Service may be effected on this entity at 1100 Park
Place, Suite 200, San Mateo, CA 94403 Attention: Legal Department. Telephone (650) 655-7800.
13. PEST CONTROL:
(a) The Premises and/or the Property is covered by a contract for regular pest control service. Pursuant to applicable law,
concurrently with signing this Lease, you are being provided with a copy of the legally required notice provided by the registered
pest control company entitled Pesticide Notice/Disclosure.
(b) Resident and Landlord both have inspected the Premises prior to leasing and acknowledge there is no visible evidence of the
presence or infestation of insects or vermin, including bedbugs, in the Premises. Resident agrees to inspect all personal
belongings for signs of bedbugs and other insects or vermin prior to bringing personal belongings into the unit and further agrees
not to bring into the Premises any belongings which Resident suspects may be infested with bedbugs, insects or other vermin.
(c) Resident agrees to maintain the cleanliness of the Premises in a sanitary condition and keep it free and clear of all rubbish,
undisposed food items (including pet food) and overcrowding of furniture, possessions and other items in such a manner that
prevents the occurrence of an infestation of insects, bedbugs or vermin. Resident agrees to report, in writing, any suspected
infestations of bedbugs, ants, fleas, roaches, or other insects or vermin immediately to Landlord.
(d) If the premises is not maintained by the Resident in a sanitary condition as described in subparagraph (c) above or Resident
allows individuals or items carrying bedbugs, fleas, roaches or other insects or vermin into the Premises, or has an infestation
that cannot be traced to another source, the resulting infestation will be deemed damage to the Premises and Resident will be
responsible for all costs of treatment to the Premises, their personal belongings and surrounding units as necessary to eradicate
the infestation (costs including but not limited to lost rents, pest control services, and tenant relocation). The choice of treatment
shall be at the discretion of Landlord in consultation with Landlord's pest control vendor.
(e) Resident acknowledges that pest or insect infestations may occur from time-to-time through no fault of the Landlord and Landlord
does not guarantee a pest or insect free environment. Landlord shall not be liable for naturally occurring conditions which might
attract pests or insects, and Resident releases and waives any right to sue Landlord for claims resulting in any physical injury,
illness or economic loss which Resident may suffer as a result of or incidental to pests or insects at or near the Property. Resident
agrees to timely cooperate with all pest control efforts at and within the Premises and the Property. Resident shall follow all
instructions from Landlord and/or Landlord's pest control company with respect to treatment and eradication whether infestation
is in Resident's unit, another unit or elsewhere on the Property at Resident’s sole expense. Resident shall make arrangements
to dispose of any furniture or other items infested with pests. Such items may not be disposed of at the Property. If the Resident
fails to cooperate in a timely manner, Resident may bear additional responsibility for the cost associated with treating neighboring
residents or other vermin.
14. INFORMATION ABOUT BED BUGS: Landlord hereby provides the following general information about bed bug identification,
behavior, biology, the importance of cooperation for prevention and treatment, and the importance of and for prompt written reporting
of suspected infestations to Landlord:
(a) Bed Bug Appearance: Bed bugs have six legs. Adult bed bugs have flat bodies about 1/4 of an inch in length. Their color can
vary from red and brown to copper colored. Young bed bugs are very small. Their bodies are about 1/16 of an inch in length.
They have almost no color. When a bed bug feeds, its body swells, may lengthen, and becomes bright red, sometimes making
it appear to be a different insect. Bed bugs do not fly. They can either crawl or be carried from place to place on objects, people,
or animals. Bed bugs can be hard to find and identify because they are tiny and try to stay hidden.
(b) Life Cycle and Reproduction: An average bed bug lives for about 10 months. Female bed bugs lay one to five eggs per day. Bed
bugs grow to full adulthood in about 21 days.
(c) Survival: Bed bugs can survive for months without feeding.
(d) Bed Bug Bites: Because bed bugs usually feed at night, most people are bitten in their sleep and do not realize they were bitten.
A person's reaction to insect bites is an immune response and so varies from person to person. Sometimes the red welts caused
by the bites will not be noticed until many days after a person was bitten, if at all.
(e) Common Signs and Symptoms of a Possible Bed Bug Infestation:
(i) Small red to reddish brown fecal spots on mattresses, box springs, bed frames, mattresses, linens, upholstery, or walls.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 5
(ii) Molted bed bug skins, white, sticky eggs, or empty eggshells.
(iii) Very heavily infested areas may have a characteristically sweet odor.
(iv) Red, itchy bite marks, especially on the legs, arms, and other body parts exposed while sleeping. However, some people
do not show bed bug lesions on their bodies even though bed bugs may have fed on them.
(f) More Information: For more information, see the Internet Web sites of the United States Environmental Protection Agency and
the National Pest Management Association.
(g) This Agreement requires Resident to cooperate fully with Landlord in the prevention and treatment of any infestation, including
the duty to report any signs of infestations. Prompt treatment and Resident cooperation is important when battling bed bugs.
Early reporting allows the pests to be identified and treated before the infestation spreads. As a tenant, Resident is the first line
of defense against bed bug infestations and should create living environments that deter bed bugs. Resident cooperation is
shown to expedite the control of bed bugs and to prevent spreading of infestation. This includes reducing unreasonable amounts
of clutter that creates hiding places for bed bugs, and regular checking of beds and laundering of linens.
15. ACCESS TO PREMISES: The parties agree that the provisions of Civ. Code § 1954 (and any other applicable statute or amendments
which might be enacted subsequent to the execution of this Lease) govern the rights and duties relating to Landlord's access to the
Premises. The parties further agree that Landlord or Landlord's agents may enter the Premises for any reasonable business purpose
at reasonable times. Resident agrees that, should Resident deny Landlord access to the Premises when Landlord is in compliance
with statutory requirements and entitled to access, any such denial of access shall be deemed a material breach of this Lease.
16. MISSTATEMENTS ON APPLICATION: Resident has completed an application in connection with executing this Lease. Landlord has
relied upon the statements set forth in said application in deciding to rent the Premises to Resident. Resident agrees any misstatements
of fact in the Resident's application shall be deemed a material and incurable breach of this Lease.
17. RESIDENTIAL USE OF PREMISES: Resident agrees that the Premises are rented for residential use only unless the Parties have
executed a separate Live Work Addendum. Resident shall not use the Premises as a business address, nor shall Resident conduct
any business activities on the Premises. Conducting business activities includes, without limitation, using the Premises as a mailing
address for a business enterprise, having a business telephone line in the Premises, having business clients meet with Resident at
the Premises, having business stationery setting forth the address of the Premises as a business address, assembling or
manufacturing any product upon the Premises, or otherwise holding out the Premises as the address of any business. Resident may,
however, to the extent consistent with the restrictions set forth in this Paragraph, use a portion of the Premises as a "home office."
Nothing set forth herein shall be deemed as disallowing any use of the Premises that cannot be prohibited legally.
18. ASSIGNMENT AND SUBLETTING: Resident shall not assign this Lease nor sublet all or any part of the Premises. Permitting any
person to occupy the Premises who is not named as a Resident in this Lease or authorized to occupy the Premises pursuant to this
Lease shall be deemed an improper subletting of the Premises and shall subject the tenancy to termination. Use of home-sharing or
short-term rental websites is a violation of this Paragraph. Any attempted subletting or assignment in violation of this provision shall
be voidable at Landlord's discretion. Any assignment or subletting, including through home-sharing or short-term rental platforms, may
be treated by the Landlord as a non-curable material breach of this lease.
19. CONDITION OF PREMISES-ALTERATIONS: Resident has inspected and accepts the Premises, and all improvements, furnishings
and fixtures therein as being in good condition, and agrees to maintain the same in said condition. Any exceptions to Resident's
acceptance of the Premises must be set forth in the Move-In Inspection Report executed by the Resident and Landlord and
incorporated herein by reference. Resident agrees not to alter (including, but not limited to, installing cameras or security systems),
install fixtures or improvements in, install or remove major appliances (including but not limited to washer/dryer, dishwasher, etc.),
paint or redecorate the Premises or any part of the Property without the prior written consent of Landlord. Resident waives all rights
to make repairs at the expense of Landlord, except and only to the extent same cannot be waived by law. All costs of restoring the
Premises or Property to its prior condition resulting from Resident's violation hereof or violation by Resident guests or invitees shall be
paid by Resident within three (3) days after written demand for payment. For the purposes of safety and quiet enjoyment Resident
shall not install or use portable washers or dryers on the Premises without Landlord's prior written consent.
20. PROPOSITION 65 WARNING: The Premises as well as the common areas in and around the Community contain at least one of the
following chemical(s) known to the State of California to cause cancer and/or reproductive toxicity and for which warnings are now
required. These chemicals include, but are not limited to: tobacco smoke, lead and lead components, asbestos, formaldehyde, pool
chemicals, carbon monoxide, benzene, and gasoline or diesel engine exhaust. Based on these exposures, the following warning is
required:
WARNING: Building materials containing urea-formaldehyde resins, such as insulation, pressed wood materials, finishes, or
adhesives, on this property can expose you to chemicals including formaldehyde, which is known to the State of California to cause
cancer. Fireplaces, fire pits, barbeques, or unvented gas space heaters, natural gas-powered appliances, as well as exhaust from
motor vehicles in parking areas or from other maintenance equipment, on this property can expose you to chemicals including carbon
monoxide, which is known to the State of California to cause birth defects or other reproductive harm, and benzene, which is known
to the State of California to cause cancer and birth defects or other reproductive harm. Talk to your landlord or the building manager
about how and when you could be exposed to these chemicals in your building. For additional information go
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 6
to www.P65Warnings.ca.gov/apartments.
21. DUTY TO CLEAN AND VENTILATE: Resident hereby acknowledges that mold and mildew can grow in the Premises if the Premises
is not properly maintained and ventilated. Resident agrees to comply with the Mold Addendum which is attached to and a part of this
Lease.
22. LIABILITY/INDEMNIFICATION/HOLD HARMLESS:
(a) Landlord does not provide or guarantee a noise-free environment. Living in a community means that it is likely Resident will be
able to hear sounds common to a community environment while inside the Premises. While Landlord will attempt to enforce quiet
hours, the provision of such quiet hours shall not be deemed a guarantee of any kind that Resident will not be exposed to common
community noise while on the Property and in the Premises.
(b) Resident agrees that the Agreement will not terminate and Landlord will not be liable for any interruption of services or
accommodations to Resident caused by casualty, strike, riot, orders or acts of public authorities, acts of third parties, including
other residents, or any other cause beyond Landlord's control.
(c) Resident agrees to hold harmless, protect, indemnify, and defend Landlord from and against any claims arising out of or relating
to the use, occupancy or maintenance of the Premises by Resident, whether such claims arise during and/or after Resident’s
tenancy. Resident agrees Landlord shall have the right to appoint defense counsel, at Resident's expense, in the event of any
such claim against Landlord. Any insurance obtained by Resident or Landlord will not limit Resident's liability, and Resident will
be responsible for the payment of any deductible if there is a covered loss.
23. SUBORDINATION: This Lease and all rights of Resident arising hereunder are expressly agreed to be subject and subordinate in all
respects to the lien of any present or future mortgages which are or may be placed upon the Property by Landlord or assigns of
Landlord and to all other rights acquired by the holder of any such mortgage(s).
24. SUCCESSORS IN INTEREST: If the Property is sold or the ownership interest is otherwise transferred, the successor in interest of
Landlord shall be deemed the assignee of all rights arising hereunder, and shall be entitled to enforce the provisions of this Lease as
necessary against Resident. Nothing in this provision shall be construed as conflicting or superseding the foregoing
"SUBORDINATION" clause or as requiring a continuation of the tenancy in the event of a foreclosure or other involuntary transfer of
ownership.
25. COMPLIANCE WITH APPLICABLE LAWS: Resident agrees not to use or permit the Premises to be used for any purpose which
violates local, state or federal law. Resident further agrees to defend Landlord against any claims arising from, or relating to, and
reimburse and indemnify Landlord for all claims, loss, damage, fines and penalties alleged against or incurred by Landlord as a result
of, Resident's alleged or actual violation of any statute, ordinance, regulation or other governmental restriction.
26. COMPLIANCE WITH COMMUNITY HANDBOOK: Resident acknowledges receipt of a copy of the Community Handbook
("Handbook"), which is incorporated into and made a part of this Lease. Resident agrees to abide by said Handbook in all respects.
Any Handbook terms may be changed on thirty (30) days' notice, and Resident agrees to abide by any such changes. Failure to
comply with the Handbook shall be deemed a breach of this Lease.
27. NO SOLICITING: Solicitation is prohibited in the Community. Except as prohibited by applicable law, soliciting of any kind by Resident,
Resident's guests or Resident's invitees is a material violation of this Agreement.
28. CONDUCT OF RESIDENT:
(a) Resident agrees not to harass, annoy, or endanger any other Resident, neighbor or other person, or create or maintain a
nuisance, or disturb the peace or solitude or quiet enjoyment of any other Resident, neighbor or other person, or commit waste
in or about the Premises.
(b) Resident agrees not to harass, verbally abuse, denigrate, endanger or otherwise disrespect Landlord's employees, agents and/or
contractors or interfere with the operations of the Property or the work of Landlord's employees or agents.
(c) Certain acts are contrary to the safety, well-being, peace, and enjoyment of the other Residents of the Property. These include,
but are not limited to, the use or exhibition of firearms or ammunition and operating drones with cameras or other photograph or
video capability, or any other flying remote-controlled device with such capabilities in any common areas of the Property. Such
acts are prohibited.
(d) Resident agrees not to deface or damage any part of the Premises or the Community or permit the same to be done, or keep
any flammable or explosive materials or any substance considered dangerous, hazardous or toxic under any governmental law
or regulation in the Premises.
(e) Resident agrees not to do or permit anything to be done in the Premises that Landlord deems hazardous or which will cause a
cancellation of or an increase in the premiums for any insurance for the Community.
(f) Resident is responsible for the conduct of Resident's guests or invitees while they are on the Property as well as all household
members (including minors).
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 7
(g) A Resident conducting any of the activities set forth in this Paragraph, or who allows his or her guests, invitees or household
members (including minors) to conduct any of the activities set forth in this Paragraph shall have materially and incurably
breached this Agreement.
29. ANIMALS: No animals are permitted on the Property or the Premises without the prior written consent of the Landlord and Resident’s
execution of an Animal Addendum. Any such consent may be revoked at any time, with or without cause, by giving three (3) days’
written notice. The presence of any pets for which written permission has not been given or which, if given, is not currently in force,
even if such pets are "just visiting", shall be deemed a material breach of this Lease. If Resident has a pet without the written consent
of Landlord in addition to all other remedies of Landlord, Resident agrees to pay within three (3) days of written demand any and all
carpet cleaning charges and fumigation costs. Accommodation Animals are not considered pets, but written permission must be
granted, and an Animal Addendum executed before an accommodation animal is brought onto the Premises. A disabled individual
who requires an animal in order to be able to use and enjoy the Premises or the Property shall comply with Paragraph 53.
30. LIQUID-FILLED FURNITURE AND AQUARIUMS: Waterbeds and other liquid-filled furniture are allowed only under in compliance
with Civ. Code § 1940.5. No aquariums over ten (10) gallons are permitted without prior written consent of Landlord. If Resident installs
any liquid-filled furniture, Landlord has the right to increase the Security Deposit by an amount to be determined in the written
authorization, which in no event shall be more than one-half of one month's rent.
31. SMOKE DETECTORS: Resident acknowledges that the Premises are equipped with an operable smoke detector(s). Resident agrees
to not interfere with the presence or operability of such smoke detectors and to report immediately to Landlord, in writing, any defects
in the condition of any smoke detectors. Resident further agrees that, if the smoke detector(s) is/are battery operated, pursuant to Civ.
Code § 1942.1, as part of the consideration of the rental, Resident assumes responsibility to: (a) ensure the battery is in operating
condition at all times; and (b) replace the battery as needed. Under no circumstances shall Resident remove the battery of a smoke
detector without immediately replacing the battery with a new one.
32. FIRE SPRINKLER(S): If the Premises is equipped with fire sprinklers, Resident agrees not to interfere with their operation in any way.
The following actions are prohibited: throwing items at the sprinklers, hanging items on the sprinklers, painting the sprinklers, blocking
areas around sprinklers and tapping into or otherwise blocking water lines to sprinklers. Resident shall immediately report to Landlord
any broken or damaged sprinklers in the Premises,
33. CARBON-MONOXIDE DEVICE(S): If a carbon-monoxide device has been installed within the Premises, Resident acknowledges that
the carbon-monoxide device was operable at the time Resident took possession of the Premises. Resident is responsible for notifying
Landlord if Resident becomes aware of an inoperable or deficient carbon-monoxide device within the Premises. Landlord shall correct
any reported deficiencies or inoperabilities in the carbon-monoxide device. Resident agrees to not interfere with the presence or
operability of any carbon-monoxide device. Resident further agrees that, if the carbon-monoxide device(s) is battery operated,
pursuant to Civ. Code § 1942.1, as part of the consideration of the rental, Resident assumes responsibility to: (a) ensure the battery
is in operating condition at all times; and (b) replace the battery as needed. Under no circumstances shall Resident remove the battery
of a carbon-monoxide device without immediately replacing the battery with a new one.
34. EMINENT DOMAIN OR CONDEMNATION: Should the Premises or the land on which the Premises are located, or any part thereof,
or any portion of the Community, be condemned or taken for public use, then Landlord shall be entitled to receive any and all just
compensation offered or awarded, and Resident shall not be entitled to receive any amount of any settlement or award of
compensation arising out of any such eminent domain or condemnation.
35. RENOVATIONS AND REPAIRS:
(a) Landlord may undertake renovations, improvements and/or repairs to the Premises from time to time that may require Landlord
or Landlord's agent to enter the Premises and may also require Resident to vacate the Premises for any length of time. Resident
must allow such entry and must vacate the Premises as needed and otherwise cooperate with Landlord in its efforts to perform
the work. To the extent possible, Landlord shall give Resident written notice of the need to enter the Premises and potentially
vacate the Premises, which notice shall include Landlord's best estimation of the length of time Landlord anticipates Resident
will need to be absent from the Premises.
(b) If the renovations, improvements and/or repairs are required because of the conduct of Resident or the conduct of Resident's
household, invitees or guests (such as misuse of plumbing, causing a fire, etc.), then Landlord shall be relieved of any obligation
to provide or pay for alternative accommodations and Resident shall remain responsible for both rent and the cost of alternative
lodging during the time when Resident must vacate the Premises for any work to be completed. Resident shall be fully liable for
all loss and/or destruction, whether partial or whole, caused by Resident or any of Resident's invitees or guests.
36. DUTY TO COOPERATE: Failure to vacate upon Landlord notice or return to the Premises or otherwise cooperate with Landlord's
efforts to conduct renovations, improvements and/or repairs at the Property is a material breach of this Lease and grounds for
termination of this Agreement.
37. VEHICLES: Resident agrees to register all vehicles with the management and comply with the Community Handbook and Handbook
Provisions, addenda to this Lease and all posted signs related to vehicles and parking on the Property.
38. CRIMINAL CONDUCT PROHIBITED:
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 8
(a) Resident and Authorized Occupants, guests, and invitees, whether on or off of the property, are prohibited from engaging in any
criminal and/or unlawful activity, from engaging in any act intended to facilitate criminal and/or unlawful activity, and/or permitting
the dwelling unit to be used for criminal and/or unlawful activity. Resident agrees to be responsible for the actions of Authorized
Occupants, guests and invitees, regardless of whether Resident knew or should have known about any such actions.
(b) ANY VIOLATION OF THE ABOVE PROVISION SHALL BE A MATERIAL AND IRREPARABLE VIOLATION OF THE LEASE
AND GOOD CAUSE FOR IMMEDIATE TERMINATION OF RESIDENT'S TENANCY. Landlord may, in its sole discretion,
determine whether a violation has occurred and need not await any court or law enforcement determination before determining
to terminate Resident's tenancy under this Paragraph.
(c) Resident hereby authorizes property management/owner to use police generated reports for any such violation as reliable direct
evidence, and/or as business records as a hearsay exception, in all eviction hearings.
39. SAFETY CONCERNS:
(a) Landlord makes no representations or guarantees to Resident concerning the security of the Premises or the Community,
including, but not limited to individual units, common areas and mail areas. Landlord is under no obligation to Resident to provide
any security measure or take any action not required by statute. The presence of courtesy patrols, patrol cars, access gates,
surveillance cameras or other deterrents do not guarantee that crime can or will be prevented. Resident is responsible for
planning and taking action with respect to the safety of Resident and their property as if such systems and deterrents did not
exist.
(b) Landlord does not accept packages, letters, or other deliveries (collectively “Deliveries”) on behalf of Resident. Resident
acknowledges that Landlord does not accept any responsibility or liability for any lost, stolen, and/or damaged, Deliveries and
Resident agrees to hold Landlord and Landlord's agents harmless from any loss or damage related to any of Resident's
Deliveries.
(c) Landlord may install surveillance cameras in some of the common areas of the Property. These cameras may or may not be
monitored and the footage recorded by these cameras may or may not be kept by Landlord for any length of time. Landlord may
remove such cameras, or install additional cameras, at any time without notice to Resident. Recordings made by surveillance
equipment, if any, are the sole and exclusive property of Landlord.
(d) Landlord has no obligation to obtain criminal background checks on any existing or future Resident and bears no responsibility
or liability related to the criminal background or actions (whether past, present or future) of any person, even if Landlord has
actually run a criminal background check on applicants. Resident shall not rely on the fact that Landlord may have run a criminal
background check on Resident or any other applicant when deciding whether to enter into this Agreement. Landlord has not
made and does not make any representations as to the background of any existing or future Resident.
(e) Resident agrees to report immediately all suspected or actual criminal activity on or near the Property to the appropriate local
law enforcement agencies and, after doing so, to Landlord, and shall provide Landlord with such law enforcement agency's
incident report number and incident report upon request.
40. MEGAN'S LAW DATABASE:
(a) Notice: Pursuant to California Penal Code (“Penal Code”) § 290.46, information about specified registered sex offenders is made
available to the public via an internet web site maintained by the Department of Justice at www.meganslaw.ca.gov. Depending
on an offender's criminal history, this information will include either the address at which the offender resides or the community
of residence and ZIP Code in which he or she resides.
(b) Since the information is equally available to Resident and Landlord, and Landlord cannot discriminate against registered sex
offenders pursuant to Penal Code § 290.46 et seq., Landlord has not made any inquiry of any applicant or resident as to whether
he or she is a registered sex offender. Resident is advised that Landlord may not notify Resident if Landlord learns or is advised
that a registered sex offender is living in the Community. The existence of registered sex offenders in the Community is not
grounds for terminating this Agreement.
41. OPTION TO TERMINATE: Resident is expected to remain a Resident for the entire term specified in this Lease. If Resident fails to
do so, Resident will be responsible to Landlord for all damages provided by law, including (but not limited to) rent due through the end
of the Lease term, minus rents paid by a replacement tenant (if any). This amount will vary depending upon how long it takes the
Landlord to find a replacement tenant. Therefore, this amount cannot be determined in advance and it is difficult to estimate.
(a) To avoid this uncertainty, Resident may choose to exercise an early termination option. Resident may choose to pay a flat fee in
advance to terminate the lease early, rather than remaining liable for rent due through the end of the lease term. To exercise this
option, Resident must deliver to Manager:
(i) A written notice stating that Resident has elected to exercise this option;
(ii) An early termination option fee in the amount of $9,178.00 (“Early Termination Fee”) and reimbursement of all move-in
concessions as provided in any concession agreement executed by the Parties; and
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 9
(iii) Rent and other amounts due through the accelerated termination date.
(b) After making a reasonable endeavor to estimate accurately the approximate costs associated with an early termination of the
lease, which the Parties agree is difficult or impossible to ascertain at the inception of this Lease since we cannot predict at this
time how long it will take to prepare and relet the Premises at some future date or the costs associated with marketing the
Premises, Resident and Landlord agree a termination charge equal to the Early Termination Fee is presumed to be the amount
of damage suffered by Landlord if Resident elects to terminate this Agreement before the termination date set forth in the
Agreement.
(c) When Landlord has received the written notice and payment, and has signed the notice, the Lease termination date will be
amended. The new termination date will be the date specified in the notice which must be at least thirty (30) days after the written
election and payment are given to Landlord.
(d) Exercise of the early termination option will affect only Resident's rent obligations after the accelerated termination date; Resident
must comply with all other Lease obligations.
(e) The notice will not accelerate the termination date if:
(i) Resident is in default under the lease at the time that Resident gives notice of Resident's exercise of the option;
(ii) Resident provides the notice unaccompanied by the fee above; or
(iii) Resident does not properly exercise the early termination option by following the procedure specified above, but vacates the
property before the termination date specified in the Lease.
42. ENTIRE AGREEMENT: This Lease, including all addenda and the Handbook, set forth the entire agreement among the Parties with
respect to the matters set forth in it. It shall not be altered nor modified unless such alteration or modification is in writing and signed
by all signatories to this Lease, unless the change is required by law, is the result of an error or omission by Landlord, or Landlord
provides the required notice for the change as required by law. No verbal agreements or representations have been made or relied
upon by either party or any agent or employee of either party, and neither party nor any agent or employee of either party is entitled
to alter any provisions of this Lease by any verbal representations or agreements to be made subsequent to the execution of this
Lease. The foregoing notwithstanding, if Resident holds over after the expiration of the Lease term pursuant to paragraph 5, Landlord
may change any provision of this Lease without the consent of Resident in the manner prescribed by Civ. Code § 827.
43. PARAGRAPH HEADINGS: The paragraph headings are inserted only for convenience and are not intended to define or limit the
scope or intent of any clause.
44. SEVERABILITY AND PROVISIONS REQUIRED BY LAW: If a provision or paragraph of this Lease is legally invalid, or declared by
a court to be unenforceable, such provision or paragraph will be deemed deleted and the rest of this Lease will remain in effect. To
the extent any provision of this Agreement is in direct conflict with any provisions of applicable law, such provision is hereby deleted.
Any provision specifically required by applicable law which is not included in this Lease is hereby inserted as an additional provision
of this Lease, but only to the extent required by applicable law and then only so long as the provision of the applicable law is not
repealed or held invalid by a court of competent jurisdiction.
45. EVENTS OF DEFAULT: Resident shall be guilty of material breach of this Lease if Resident: (a) fails to pay any rent or other sum
payable under this Lease on the date it becomes due; (b) breaches any other provision, term, covenant or condition of this Lease; (c)
vacates or abandons the Premises before expiration of the full term of this Lease, or any extension of the term; (d) permits the leasehold
interest of Resident to be levied upon or attached by process of law; or (e) makes an assignment for the benefit of creditors.
46. WAIVER: Landlord's failure to require strict compliance with any provision of this Lease or to exercise any rights arising under this
Lease shall not be deemed a waiver of Landlord's right to enforce any such provision or to insist upon any such right. The fact that
Landlord may have accepted late payment(s) on one or more occasions shall not be deemed a waiver of Landlord's right to insist upon
timely payment of rent nor to exercise any remedy available for late payment of rent. Acceptance of rent following a breach of this
Lease shall not be deemed to constitute a waiver of such breach. No custom or practice which may develop between the Parties in
the course of tenancy shall be construed to waive the right of Landlord to enforce any provision of this Lease.
47. USE OF PERSONAL INFORMATION: For details on what personal information Landlord collects and for what purposes, and
Resident’s privacy rights and how to exercise them, visit Essex's Privacy Policy at www.essexapartmenthomes.com/privacy-policy.
48. TIME IS OF THE ESSENCE: Time is of the essence with respect to the provisions of this Lease. This provision shall be interpreted in
its strictest sense irrespective of the relative hardship to the Parties.
49. ATTORNEY'S FEES: In the event of any litigation relating to this Agreement or the rights or liabilities of any party arising under this
Agreement, the prevailing party of such litigation shall be entitled to its costs, including reasonable attorneys' fees, incurred in such
litigation, not to exceed a maximum total of two thousand dollars ($2,000) fees and costs. If any such litigation is dismissed prior to
trial, the parties agree that there shall be no prevailing party for purposes of an award of attorney's fees and/or costs. An unlawful
detainer action shall be considered an action relating to this Lease and thus subject to this provision.
50. SURRENDER: Upon expiration or termination of this Lease, Resident shall vacate and surrender the Premises to Landlord vacant of
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 10
all occupants and in the condition required to be maintained under this Agreement. Resident shall also return all keys and remote
access devices (if applicable) to Landlord or pay Landlord's then applicable charge for non-returned keys and remotes (if applicable).
51. ATTACHMENTS/ADDENDA: Resident acknowledges receipt of a copy of the attachments/addenda listed below, which are
incorporated into and made part of this Lease. Resident agrees to abide by said attachments/addenda in all respects. Any failure to
comply with any of the attachments or addenda shall be deemed a breach of this Lease.
Amenities Activities
Community Handbook
Parking Agreement
Renter’s Insurance Addendum
SmartRent Addendum
Key Addendum
Utility Addendum
Mold Addendum - California
Pesticide Addendum
Flood Zone
California Tenant Act of 2019 Addendum
Santa Cruz Security Deposit Addendum
Smoking Policy Addendum
52. NON-DISCRIMINATION: There shall be no discrimination against or segregation of any persons on account of race, color, national
origin, ancestry, creed, religion, sex and gender, gender identity, gender expression (including transgender individuals who are
transitioning, have transitioned, or are perceived to be transitioning to the gender with which they identify), sexual orientation, genetic
information, marital status(including registered domestic partnership status), familial status, age, source of income, national origin,
ancestry, immigration status, citizenship, primary language, handicap, physical or mental disability, medical condition, genetic
information, Civil Air Patrol status, military and veteran status or any other protected classification under state or federal law, in the
sale, lease, sublease, transfer, use, occupancy, tenure or enjoyment of Premises, nor shall the Landlord or any person claiming
under or through Landlord establish or permit any such practice or practices of discrimination or segregation with reference to the
selection, location, number, use or occupancy of tenants, lessees, or vendees in the Premises, or any other consideration made
unlawful by federal, state, or local laws, and/or retaliation for protesting illegal discrimination related to one of these categories.
53. REQUESTS FOR ACCOMMODATIONS OR MODIFICATIONS: A disabled person, for all purposes under this Lease, shall be
provided reasonable accommodations or reasonable modifications to the extent necessary to provide the disabled person with an
opportunity to use and occupy the Premises in a manner equal to that of a non-disabled person. If Resident believes Resident or a
member of Resident's household requires an accommodation or modification as a result of a disability, Resident should contact
Landlord to begin the interactive process.
54. CREDIT REPORTS: Resident expressly authorizes Landlord and/or Landlord’s agent to disclose information about Resident and
Resident’s tenancy to credit reporting agencies including, but not limited to, the amount and timing of payments due pursuant to the
Lease including payment of Monthly Base Rent, good behavior, problematic behavior, and any debt outstanding, which may then be
used in a tenant record, credit report and/or credit score for the Resident. For the avoidance of doubt, Resident’s failure to pay the
full amount(s) owed to Landlord on the date such amount(s) is due pursuant to the Lease will result in a negative credit report
submitted to a credit reporting agency. Further, Resident expressly authorizes Landlord and/or Landlord’s agent to obtain Resident’s
consumer credit report, which Landlord may use if attempting to collect past due rent payments, late fees, or other charges from
Resident, both during the term of the Lease and thereafter.
55. CAMERAS: Resident acknowledges and agrees that Landlord shall have the right, but not the obligation, to use and/or install
cameras at the Property and Resident hereby consents to Landlord's use of Resident's image and/or likeness, in each case for
marketing and/or surveillance purposes.
56. PERSONAL MICROMOBILITY DEVICES: E-Bikes, electric scooters, electric hoverboards or other Personal Micromobility Devices
of any kind may not be stored or charged anywhere on the Premises or in the Unit, except as provided below.
(a) Personal Micromobility Device means a device with both of the following characteristics: (A) it is powered by the physical exertion
of the rider or an electric motor; and (B) it is designed to transport one individual or one adult accompanied by up to three minors.
(b) Resident may store and recharge up to one Personal Micromobility Device in their Unit for each person occupying the Unit if the
Personal Micromobility Device meets the requirements in subparagraphs (i) or (ii) below. If the Personal Micromobility Device
only meets subparagraph (iii) below, it may be stored, but not charged in the Unit.
(i) The Personal Micromobility Device is not powered by an electric motor.
(ii) The Personal Micromobility Device complies with the following safety standards: (a) for e-bikes, UL 2849, the Standard for
Electrical Systems for e-bikes, as recognized by the United States Consumer Product Safety Commission, or EN 15194,
the European Standard for electrically powered assisted cycles (EPAC Bicycles) or (b) for e-scooters, UL 2272, the
Standard for Electrical Systems for Personal E-Mobility Devices, as recognized by the United States Consumer Product
Safety Commission, or EN 17128, the European Standard for personal light electric vehicles (PLEV).
(iii) The Personal Micromobility Device is insured by Resident under an insurance policy covering storage of the Personal
Micromobility Device within Resident’s Unit. Charging the Personal Micromobility Device in Unit is prohibited if the Personal
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 11
Micromobility Device does not meet the safety standards in (ii) above even if the Personal Micromobility Device is insured
by Resident as required by this subparagraph. Resident must promptly provide proof of such insurance to the Landlord by
demand.
(c) Repair or maintenance of batteries and motors of Personal Micromobility Devices is prohibited within the Unit. However, a
Resident may change a flat tire or adjust the brakes on a Personal Micromobility Device within the Unit.
(d) Notwithstanding the provisions above, any Personal Micromobility Device must be stored in compliance with applicable fire code
and in compliance with the California Office of State Fire Marshal Information Bulletin 24-001 regarding lithium-ion battery safety,
issued January 23, 2024, or any updated guidance issued by the California Office of the State Fire Marshal regarding lithium-
ion battery safety.
(e) This Paragraph does not limit the rights and remedies available to disabled persons under federal or state law.
57. SIGNATORIES: The individuals signing below as "Resident," whether or not in actual possession of the Premises, are jointly and
severally responsible for all obligations arising under this Lease, including all obligations to pay rent. This Lease shall not be
considered to be in full force and effect until signed by Landlord or Landlord's authorized agent. Landlord may, without liability, refuse
to enter into this Lease and may refuse to allow Resident to occupy the Premises at any time prior to Landlord signing this Lease.
Each Resident shall be fully liable for all obligations arising under this Lease, and Landlord may enforce the provisions of this Lease
as against Resident if, for any reason or by any means, Resident obtains access to the Premises before such time as this Lease
has been signed by Landlord or Landlord's authorized agent.
THE UNDERSIGNED EXPRESSLY UNDERSTAND(S) AND ACKNOWLEDGES THAT PARAGRAPH 5 CONTAINS PROVISIONS
UNDER WHICH THIS LEASE MAY AUTOMATICALLY RENEW AS A TENANCY FOR SUCCESSIVE TERMS MATCHING THE
SHORTER OF THE INITIAL LEASE TERM IDENTIFIED IN PARAGRAPH 4 OR 12 MONTHS UPON THE EXPIRATION OF THE
LEASE IF RESIDENT REMAINS IN POSSESSION AFTER THE EXPIRATION OF THE LEASE OR FAILS TO GIVE NOTICE OF
RESIDENT'S INTENT NOT TO RENEW OR EXTEND BEFORE THE EXPIRATION OF THE LEASE.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 12
RECREATIONAL FACILITY USE AND ACTIVITIES PARTICIPATION
ADDENDUM
This Recreational Facilities Use and Activities Participation Addendum ("Addendum") dated 07/31/2025 is attached to and made a part
of the lease agreement dated 07/31/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as
agent for Owner ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and
collectively referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060
("Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). Landlord and Resident
are collectively referred to herein as "Parties." All terms not specifically defined herein shall have the same definition as found in the
Lease. Resident and Landlord agree as follows:
Resident, as well as Resident’s Authorized Occupants, guests, and/or invitees (collectively “Guests”), may have access to recreational
facilities at the Community, and/or Shared Amenities (defined below, if any) at neighboring properties, which may include a fitness
center, pool, spa, sauna, business center, billiard room, tanning equipment or similar amenities (collectively "Recreational Facilities.").
Landlord may offer Resident the opportunity to participate in activities, events, and/or services, such as socials, fitness classes, and
other optional activities, which may or may not require payment of a fee prior to participation ("Activities").
Resident, for good and valuable consideration, including, but not limited to the opportunity to use the Recreational Facilities and
participate in Activities, hereby acknowledges and agrees to the following terms governing use of the Recreational Facilities and
participation in Activities at the Community:
1. RULES: To use the Recreational Facilities and/or participate in the Activities, Resident must be in material compliance with
Resident’s Lease including, but not limited to, current on all amounts due and payable under the Lease. Resident further agrees to
abide by all of the rules and regulations which may be adopted from time to time, with or without notice to Resident, by Landlord,
which may be set forth in the Community Handbook, posted at the Recreational Facilities, or otherwise conveyed to Resident
verbally or in writing by Landlord by and through its employees or agents (“Rules”). Any Resident asked to leave a Recreational
Facility and/or Activity for failure to comply with Resident’s Lease or violation of the Rules shall not be deemed a reduction in
housing service and shall not be grounds for a reduction in rent.
2. ASSUMPTION OF RISK: Resident understands and acknowledges that accidents sometimes occur during the use of the
Recreational Facilities and/or participation in Activities. Resident further understands and acknowledges that Resident’s use of the
Recreational Facilities and/or participation in the Activities could result in loss of or damage to Resident’s property, illness, serious
injury to Resident’s body or to others, and/or Resident’s death. Resident has been informed of the risks. Understanding and
acknowledging all possible risks, Resident hereby knowingly, voluntarily and willingly assumes all risks and dangers
associated with Resident's use of the Recreational Facilities and/or participation in the Activities up to and including
personal injury or death.
3. AUTHORIZED OCCUPANTS, GUESTS, INVITEES: The terms of this Addendum shall also apply to Resident’s Authorized
Occupants, guests, and/or invitees, together with the heirs, assigns, estates and legal representatives of them all, (collectively
“Guests”). Resident’s Guests must be accompanied by a resident of the Community at all times. Residents are responsible for all
behavior of their Guests using the Recreational Facilities and/or participating in the Activities. Resident further acknowledges and
agrees that some Recreational Facilities and/or Activities may not be open to Guests, at Landlord’s sole discretion. Resident shall
be solely responsible for the compliance of the Guests with the Lease, this Addendum, and the Rules.
4. CHANGES IN ACTIVITIES AND RECREATIONAL FACILITIES: Landlord may change, expand, remove or add Recreational
Facilities at any time in its sole discretion. There is no set schedule of Activities and Landlord may decide to discontinue Activities
at any time without notice.
5. ALCOHOL: At some Activities, alcohol may be served and/or purchased. Resident must be 21 or older to consume alcoholic
beverages. Participants under the age of 18 must be with a responsible adult to attend any functions at which alcohol is served.
6. VOLUNTARY PARTICIPATION: Participation in Activities and use of Recreational Facilities is purely voluntary and at the
Resident's or Resident’s Guest’s own risk. Prior to participating in any Activity or using any Recreational Facility or Shared Facility,
Resident and Resident’s Guests agree to fully ascertain, appreciate and understand the risks and assume same.
7. WAIVER AND RELEASE: In consideration of being allowed to use the Recreational Facilities and participate in the Activities, and
having assumed all risks of same, Resident hereby expressly releases, waives, covenants not to sue the Owner of the Property,
owner of the Recreational Facilities, Essex Property Trust, Inc., Essex Management Corporation, each of their affiliates and
subsidiaries and each and every officer, agent, and employee of each of the foregoing entities (collectively, the "Released
Parties") from all claims, causes of action, or demands of every kind which Participant may have in the future or that any person
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 13
claiming through Resident may have in the future against any of the Released Parties by reason of any injury to person or
property, or death, directly or indirectly resulting from, or in connection with, Resident’s or Resident’s Guest’s use of the
Recreational Facilities or participation in the Activities.
8. INDEMNITY: Resident agrees to indemnify, defend and hold harmless each and every one of the Released Parties for any liability
of any kind whatsoever arising from Resident’s and/or Resident’s Guest’s use of the Recreational Facilities and/or participation in
the Activities, except for claims arising out the gross negligence or willful misconduct of one of the Released Parties in failing to
correct a dangerous situation at or in the Recreational Facilities after receiving notice of same.
9. SEVERABILITY: If any provision of this Addendum is invalid or unenforceable under applicable law, such provision shall be
ineffective to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this
Addendum.
ACKNOWLEDGMENT AND UNDERSTANDING. By signing below, Resident certifies that Resident is at least
eighteen (18) years of age, has carefully read this RECREATIONAL FACILITIES USE AND ACTIVITIES
PARTICIPATION ADDENDUM. Resident fully understands its terms, and understands that he/she has given
up substantial rights by signing this Addendum and has signed it freely and voluntarily without any
inducements, coercion, assurance or guarantee being made to me. RESIDENT INTENDS RESIDENT’S
SIGNATURE TO BE A COMPLETE AND UNCONDITIONAL RELEASE, WAIVER AND AGREEMENT AS STATED
HEREIN OF ALL LIABILITY TO THE GREATEST EXTENT ALLOWED BY LAW.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 14
COMMUNITY HANDBOOK
Welcome! We are honored you have chosen an Essex community for your home. At Essex, if it's important to you, it's important to us.
Our goal is to treat you with respect and make your experience here enjoyable. We strive to foster a lasting relationship and provide you
with personal service and amenities to make life a little easier.
This Community Handbook contains our policies and house rules, which help make your community a comfortable, friendly and welcoming
place for all. This Community Handbook is part of your lease agreement with us and needs to be followed the same as any other provision
of your lease. Please take time to read through this Handbook and become familiar with it. If you have any questions, don't hesitate to
contact an associate in the Community Office.
Important Contact Information
Our associates are here to assist you with any questions or concerns you may have. Please feel free to call or email during regular
business hours. If you are unable to contact us during regular business hours, which are posted on our website listed in your Lease, we
will be happy to arrange an appointment time that meets your needs. Below are some of the most common numbers you may need during
your residency with us.
Community Office
Phone: (831) 469-3620 (“Community Phone”)
Email: chestnut@essex.com
Maintenance Service
For Emergency Service Requests, please contact us via the Community Phone.
For Non-Emergency Service Requests:
Online Resident Portal: https://chestnut-street-apartments.residentservice.com
Via Phone: Call our Community Phone
IN CASE OF EMERGENCY ALWAYS CONTACT 911 FIRST IF NEEDED
Community and Unit Maintenance
Move-in Unit Inspection Form
We want you to be happy with your new home right from the start, so we'll provide you with a move-in inspection form to guide you in a
thorough inspection of your Unit. The completed form will reflect our mutual agreement as to the condition of your Unit when you move
in. If you don't fill it out and return the form within 48 hours that means nothing in your Unit needs to be repaired or cleaned.
Maintenance Services
Maintenance services are available to residents during the hours indicated at the beginning of this Handbook. Non- emergency
maintenance requests should be submitted through the Online Resident Portal listed at https://chestnut-street-
apartments.residentservice.com.
When you move in, your Unit will be fully equipped with lightbulbs in all permanent fixtures. After that, you're responsible for the
replacement of regular lightbulbs, but we'll take care of fluorescent, appliance, and exterior light fixtures. When those need replacing,
please submit a maintenance request.
Maintenance Emergencies
If you have a maintenance emergency, please immediately call the number indicated in the "Contact Information" at the beginning of this
Handbook.
What is a maintenance emergency?
• Fire, potential fire hazard, criminal activity, significant property damage, storm damage, flood, being trapped in an elevator,
no electrical power or other electrical problem, no heat, no hot water, no water at all, smell of gas or your refrigerator has
failed.
• A serious roof leak, water leak, plumbing leak, overflowing tub or flooding in your Unit.
• The only toilet in your Unit is not working or is overflowing is definitely a maintenance emergency – but please try to unclog
it with a plunger before calling.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 15
• Similarly, if your only tub or sink is broken or clogged, that is an emergency. If the water is not overflowing and/or you have
another bathroom, we will address the problem the next working day.
• Your front door, sliding glass door or windows will not lock or are broken. We want you to be safe, so please call us
immediately if your locks are not working.
• If you can't get into your Unit because the access gates or your garage door are not working, or the entrance is blocked.
If you no longer need us after calling in for a maintenance emergency, please call back so we can cancel the dispatch.
Lockout Service
We may assist with lockouts and admit any authorized occupant with appropriate identification into the Unit during office hours. Please
note that this service, if provided, will be provided for a fee. Unfortunately, we are not able to provide after-hours lockout services. Please
see the Access Cards, Keys, Remotes, Directories and Lockout Policy Addendum for more information. For properties with SmartRent
access devices, please see your SmartRent Addendum for more information.
Pest Control
Our pest control company treats the community on a regular basis. If you require additional pest control assistance, contact the
Community Office. We will be happy to help you get rid of any unwanted insect or pests.
Building Exterior and Grounds
We try to keep the grounds and public areas clean, neat and attractive for everyone to enjoy. Help us stay beautiful:
• Please do not leave personal belongings in the common areas. When we come across something that's been left out all
night, we have to assume it is trash and dispose of it properly.
• Please make sure your garbage goes straight from your Unit to the community garbage bins, and to clear personal
belongings from outside your front door.
• Please show respect for landscaped areas, shrubbery and trees. We work hard to keep the grounds looking great, and
appreciate your help in keeping them that way.
• Please keep your holiday decorations tasteful and remove them no more than a week after the holiday, local parade or
festival.
• All shopping carts should remain at the store. They are not to be brought to the Community.
• The design of our Community depends on a clean, uncluttered look to our windows. As a result, please don't place foil,
stickers, decals, posters, tinfoil, colored blinds or any other window treatments in window areas.
• No alterations or attachments of any kind are to be placed on or affixed to any portion of the exterior of the building. Any
objects that may deface the building are not permitted. Do not make holes in doors, exterior walls, windows or railings.
Patios and Balconies
Nothing should be placed on balcony railings and, for your safety, please limit the people and belongings on your balcony. A safe guideline
is no more than 40 pounds per square foot. While balcony sizes vary, the maximum occupancy for a 4' x 8' balcony is 6 people, plus
some standard patio furniture.
An attractive community can't exist without your cooperation, especially when it comes to maintaining good-looking patios and balconies.
Bicycles, approved outdoor furniture and well-kept potted plants (subject to size limitations) are the only items permitted on patios and
balconies (subject to management discretion). Leaving items outside is at your own risk; we encourage you to use appropriate storage
facilities where available. Please keep your patio (including walls and railings) free of flags, garbage containers, boxes, appliances, indoor
furniture, exercise equipment, debris, awnings, gazebos, bamboo or other privacy screens and tents.
If you have a private patio or balcony enclosed by a fence, railing, or other structure then you can use those private areas to dry laundry
so long as you comply with the following:
• No more than two drying lines or racks may be in use at any one time.
• Items may not be left on the drying lines or racks for more than 24 hours (i.e., all items must be removed within 24 hours
of being put out on the drying lines or racks).
• Drying lines or racks must be free standing (that means no, you cannot affix them to any part of the building).
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 16
• No drying lines or racks may be attached or affixed in any manner to any portion of the building, fence, railing, wall, building
support structure, or light fixtures.
• Drying lines or racks cannot be higher than the patio, balcony, or deck fence or railing.
• Drying lines or racks cannot be clearly visible from the sidewalk or street.
• Drying lines or racks cannot block entrance to or egress from the unit, create a health or safety hazard, or interfere with
walkways or utility service equipment.
• Drying lines or racks cannot interfere with the maintenance of the Community.
• Clothes may not be draped over fence or balcony railings, or hung from any building fixtures.
If you want to install plants, shades or furniture, please check with your Community Manager first. He or she can help make sure
your choices fit within your Community's guidelines and general appearance.
Satellite Dish/Antenna
We will allow you to install one (1) satellite dish or antenna (collectively referred to below as a satellite dish) for personal, private use in
the Unit under the following conditions:
• The satellite dish must be three (3) feet or less in diameter.
• The satellite dish may only be installed on the inside balcony, patio or terrace that is under your exclusive control. The
satellite dish, or any part of it, cannot extend beyond the balcony, patio or terrace railing. Allowable locations may not
provide an optimal signal, or any signal. We can't promise that the Unit will provide a suitable location for receiving a satellite
signal.
• You are prohibited from making physical modifications to the Unit and are prohibited from installing said satellite dish in the
common areas of the Community, including, but not limited to, exterior walls, roofs, window sills, common balconies or
stairways.
• You can't install the satellite dish in a manner that causes physical or structural damage to the Unit, excluding ordinary
wear and tear, including, but not limited to, holes drilled through exterior walls.
• You must install, maintain and remove said satellite dish in a manner which is consistent with industry standards.
• You must indemnify, protect and defend us against, and hold us harmless from, all claims, losses, damages, costs and
expenses, including, but not limited to, reasonable attorneys' fees, expenses and court costs relating to any personal injury
or Community damage arising from the installation, operation, maintenance and/or removal of said satellite dish.
• If requested, you must provide the Community Office with a copy of any liability insurance coverage maintained by Resident
for said satellite dish. Landlord reserves the right to require that such insurance shall name Landlord as an "additional
insured."
Personal Barbecue Grills
Due to locally enforced regulations from the International Fire Code, charcoal and propane barbecues as well as all other open-flame
cooking devices cannot be operated on combustible balconies or within 10 feet of combustible buildings. Accordingly, Residents are not
permitted to use any barbecue on the balcony, or under an overhang. Storage of these devices within your home, storage facility, garage
or balcony is also prohibited. The only exception permissible is if the cooking device is an electric grill or utilizes liquefied-petroleum
(including propane) and the gas container has a water capacity no larger than 2.5 pounds [nominal 1 pound (0.454kg) LP-gas capacity].
These accepted cooking devices have very small containers like the ones used for camping stoves.
Political Signs
A "political sign" is one that relates to any of the following: an election or legislative vote, including an election of a candidate to public
office; the initiative, referendum or recall process; and issues that are before a public commission, public board or elected local body for
a vote.
You may only post political signs in the window or door of your Unit if you comply with the following:
• The signs may not be more than 6 square feet in size; or posted or displayed in violation of any local, state or federal law.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 17
• You may not install or allow a political sign to be installed that causes any damage to or alteration of the Unit such as drilling
holes; nailing into outside walls, door frames, window sills, railings, etc.; or affixing tape or other sticky material in a way
that will cause damage to paint or other finishes.
• Resident may post and shall remove any political signs in compliance with the time limits set by the ordinance for the
jurisdiction where the Unit is located. Resident shall be solely responsible for any violation of any local ordinance. If no local
ordinance exists or if the local ordinance does not include a time limit for posting and removing political signs on private
property, political signs may not be posted more than ninety (90) days prior to the date of the election or vote to which the
sign relates and must be removed ten (10) days following the date of the election or vote.
• Resident is strictly liable for any damages or injury that results from such installation and for the cost of repairs or repainting
that may be reasonably necessary to restore the leased Unit to its condition prior to the posting of the political sign(s).
Be a Good Neighbor
Alcohol intoxication, disorderly conduct and excessive noise are not allowed in the Community. Anyone consuming alcohol at our
Community must be at least 21 years old and in the privacy of your Unit. Alcohol is allowed in common areas only when permitted or
approved by the Community Office.
Disturbances and Noises
Noise can be a nuisance and we ask all of our residents to be considerate of their neighbors when entertaining, using their television or
stereo, or using appliances or vacuum cleaners late at night. If you live in an upstairs Unit, avoid running, jumping or slamming doors. If
your Unit has some or all hard surface flooring (e.g. wood, tile, concrete), you are required to ensure at least 75% of the hard surface
flooring is covered with a carpet or rug, with a particular focus on ensuring areas of high foot traffic in your Unit are covered. Please
observe the quiet hours of your community, which are generally 10pm-7am, but may vary from community to community.
If you believe your neighbor is causing a disturbance or not observing the quiet hours, try politely talking to them before contacting the
Community Office. They probably don't realize they were bothering anyone. If their response is not satisfactory, call the Community Office
or our courtesy patrol. And if your neighbors come to you with a concern about noise coming from your Unit, please try your best to
accommodate them.
Garbage Removal
Trash is regularly removed from our garbage receptacles. Please make sure you are putting your garbage in one of them. If the receptacle
nearest you is full, please take your garbage to another one. Garbage bags left on the ground are a genuine health hazard and can attract
unwanted pests. If you regularly have trouble finding an empty garbage receptacle, report the problem to the Community Office. Also, for
your safety, once garbage is placed in a trash receptacle, please don't attempt to remove it.
• Trash must be disposed of properly, preferably in tightly tied plastic bags or closed containers. Please use a plastic bag or
trash liner to carry refuse to the dumpster or trash chutes, where provided. This prevents waste from dripping on carpet or
concrete and preserves the appearance and cleanliness of your home.
• Place all household refuse inside proper refuse containers, and do not place any items outside or around the containers.
All boxes placed in these containers must be broken down, allowing for maximum usage of this service.
• Don't be a litterbug. Make sure that papers, gum, candy wrappers or any other trash is placed in appropriate receptacles.
• If we are required to repeatedly clean up excessive trash around your Unit, we may charge you for the time spent doing so.
• Do not empty ashtrays into the parking lot or dispose of other items from vehicles by leaving them in the parking area.
• Do not put furniture or other large items in the trash. Please make other arrangements for disposing of such items. You
may be responsible for extra pickup charges due to inappropriate items in the dumpsters or dumpster area.
• If your Community has garbage chutes, use moisture-proof bags to carry waste to the trash drops on each floor to prevent
stains on the carpeting. All garbage should be deposited directly into the garbage chutes and must be completely contained
in sealed bags. We are not responsible for hauling away non-trash items such as old furniture, etc. If you have large,
oversized disposable items that do not fit in garbage chutes, where provided, please notify us. DO NOT FORCE LARGE
ITEMS INTO THE CHUTE. You will be held responsible for any cleanup costs due to garbage bag leaks, breakage or any
noted garbage trails in the Community.
• Please remember to recycle and compost where available. If you have questions about recycling and/or composting
procedures and opportunities at your Community, please ask the Community Office.
Pets
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 18
Your Community Management Team can tell you about any special restrictions, deposits, documentation or agreements required if you
have a pet. We also have a few other basic rules and guidelines.
• If you're considering a new pet and would like more information, please contact your Community Office for details.
• Most communities do not allow more than two pets per Unit.
• Certain breeds are not allowed. A full list is contained in the Animal Addendum you will need to sign before bringing an
animal home.
• We also can't allow any wild, exotic, endangered or poisonous creatures (animals, reptiles, birds, etc.) to be in residence
at your Community.
• Animals must be housebroken, spayed and neutered, and have no vicious tendencies or history of threatening or causing
physical harm to persons, property or other animals by biting, scratching, chewing, etc.
• Please make sure your animal does not disturb the quiet enjoyment of others by barking, scratching, whining, howling,
crying or in any other way.
• Don't neglect your animal. If we suspect any animal is being neglected, mistreated or abandoned, we will contact Animal
Control or a similar agency so the animal can be removed and cared for properly.
• Please watch your animals on patios or balconies – animals should not be left on patios or balconies while you are away.
And while we don't want any animals injured, you cannot enclose any outdoor space with wire or screens or similar materials
to contain the animal outdoors.
• Please keep your animal under control at all times. Dogs should be on a leash no longer than 8'. Cats must remain inside
your Unit or be leashed or in a carrier when outside.
• You are responsible for any messes your animal creates. Please clean up after your animal both in your Unit and around
the Community. If you have cats, dispose of litter in sealed trash bags in proper trash receptacles. Do not dispose of litter
in toilets.
• You are responsible for any damage your animal may cause. When you move out, if there is evidence of fleas or other
pests, you will be charged for the costs of fumigation or other appropriate treatment. Likewise, if your animal has damaged
the Unit (carpet, woodwork, paint, etc.), you are responsible for the costs of repair.
• An aquarium is fine, but if it holds more than 10 gallons of water, you'll need insurance for it.
• For rules about other types of pets or accommodation animals, please check with the Community Office. They'll be happy
to provide more information.
Weapons and Firearms
Displaying or discharging fireworks, guns, slingshots, or any type of firearm or weapon is strictly prohibited. Violation of this policy by
any resident, occupant or guest will result in the immediate termination of the lease contract.
Green Community
We require the cooperation and support of everyone in our Community in a wide range of sustainability and energy conservation
initiatives and programs. Please ensure that all household members and guests comply with all the Community's sustainability and
energy conservation practices and guidelines applicable to the Unit and the Community.
• Please operate any ENERGY STAR® rated appliances in the Unit in accordance with standard operating instructions. If
you require instructions, please reach out to the Management Office.
• Immediately notify your Community Office if any appliance in the Unit is damaged in any way or not working properly.
• Do not tamper with, interrupt or replace any energy, water, carbon reduction, or other sustainable measures installed and
maintained by Landlord, including, but not limited to, energy efficient bulbs; lighting controls, such as automatic sensors;
sun shielding blinds and devices; thermostats and/or air-conditioning/heating controls; door/window weather stripping; and
low-flow and water efficient devices, such as faucet aerators and showerheads.
• Please follow all recycling, composting and waste sorting and management practices as required by local ordinances and
in accordance with Community policies.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 19
• After using the amenities in common spaces, please turn off the lights, television, and other electrical equipment to reduce
energy usage.
Caring for Your Unit, Appliances and Plumbing
Carpet and Vinyl Floor Coverings
We recommend that you vacuum at least once a week. Using plastic trays under plants can prevent water damage and bleaching, and
acting quickly to clean up spills allows you to cope with them before they dry and become set in the carpet.
• Use only approved carpet and vinyl cleaners and agents.
• If you want to have your carpets cleaned, please let us know. We will be happy to schedule a cleaning for you (although it
generally will be at your cost).
Counter Tops
• Do not place hot vessels directly on counter tops – use a trivet or pot holder.
• Cut all food items on a cutting board instead of on the counter, or you may damage the surface.
• For Units with granite countertops, please use non-abrasive and granite-specific cleaners.
Dishwasher
• To prevent the drain from clogging, scrape your dishes before loading.
• Load dishwasher-safe plastic and wooden items in the top rack.
• Also, please only use dishwashing detergent in the dishwasher. Other types of soap will cause excessive bubbles and may
damage the floors, appliances and cabinets. If you have excess bubbles, use laundry softener to stop the bubbling and call
us so we can assist.
• Carefully load dishes to not interfere with the action of the rinsing arm.
Living Conditions
You must keep your Unit clean and uncluttered to allow easy passage throughout. Windows and doors should not be blocked. Flammable
materials may not be stored in the Unit.
We may require the removal of items, newspapers, trash, etc. that are deemed to be a fire or health hazard. Also, you may not add
appliances, such as dishwashers, washing machines, dryers, freezers, etc. to the Unit without prior written consent of the Community
Office.
Garbage Disposal
• The "garbage" disposal, is not for garbage. It's only for certain types of food waste. Nothing large should be placed in it.
• Run cold water before and during disposal operation.
• Occasionally sharpen the blades by running cold water, inserting ice cubes and operating the disposal.
• To deodorize, run cold water and insert orange or lemon peels.
• Please DO NOT use drain-cleaning chemicals. They're really rough on the pipes and the environment.
Please DO NOT dispose of bones, celery, onion peels, cornhusks, corn silks, watermelon seeds, artichoke leaves, coffee grounds,
grease, oil, fat, pasta or rice, all of which will cause clogging and damage the disposal. In addition, don't put metal, glass, cloth or fish
tank rocks down the disposal. It damages the blades. Also, take care not to drop silverware into the disposal.
• If the disposal will not operate when the switch is in the "On" position, turn the disposal off and locate and depress the red
"Reset" button on the underside of the disposal unit. If the disposal still does not operate, contact the Community Office for
help.
Refrigerator
Clean the interior and exterior of your refrigerator with a mild cleaning solution of baking soda and warm water. Avoid using any abrasive
cleansers, gritty soaps and heavy-duty cleaning agents.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 20
Sinks/Drains
Keep your drains clear by not disposing any of the following in them:
• Grease: Collect it in a container and put in the garbage.
• Paper towels/rags: Discard these in the garbage. Do not flush down the toilet.
• Excessive toilet paper: Using large amounts of toilet paper does not give it time to dissolve, resulting in overflows.
• Excess hair: Remove hair from sink or tub; do not rinse down the drain.
Microwaves
Do not put anything metal in microwaves. This includes spoons, pots and pans with metal trim, recycled paper towels which have trace
metals, aluminum foil, metal twist ties, poultry pins, meat thermometers, and Styrofoam plates (which may contain trace metals).
Washer and Dryer
If you have a washer/dryer, clean the interior and exterior with a mild solution of baking soda and warm water – please don't use abrasive,
gritty or heavy-duty cleansers. For the best performance, empty the dryer lint tray after each load. Also, please leave your washer open
when not in use to allow it to dry out and prevent mildew growth.
Fireplace
If your Unit has a fireplace, follow these basic care and safety precautions:
• Do not use flammable liquids such as gasoline, kerosene or lighter fluid.
• Burn only seasoned wood, cut to the proper length. Use only paper to start fires. Do not burn tires, trash or other items in
your fireplace.
• If you use manufactured fireplace logs, follow the manufacturer's instructions.
• Open your damper before starting a fire; always use an iron fireplace grate and keep the fireplace screen closed until all
embers are cold. It only takes a spark to start real trouble, so please be careful and stay safe.
• Dispose of the ashes when the embers are completely cold. For your safety, wait at least 48 hours for the embers to cool.
If you have a gas fireplace:
• Be sure to keep the glass clean and the vents unobstructed and able to do their job.
• NOT TO PLACE ANYTHING IN THE FIREPLACE. they are natural gas burning and there should be no wood, paper,
gasoline, kerosene or lighter fluid.
If you believe your fireplace is not working properly, please let us know so we can call a technician.
Fire Sprinklers
If there is a fire suppression sprinkler system in the ceiling of your Unit, leave the sprinkler heads alone. They are sensitive and can be
easily broken off. If they are broken off or accidentally triggered, it will cause immediate flooding in your Unit, (and possibly your neighbor's)
and you will be responsible for the cost of cleaning it up.
If a sprinkler head is broken, immediately submit an emergency maintenance service request and call the fire department to report the
breakage and minimize damages due to flooding.
Tips for Preventing Mold & Mildew
As part of your Lease, you signed a Mold Addendum. That document controls our respective legal obligations, and we wanted to provide
you with some additional tips for preventing organic growth within your Unit. You can help minimize organic growth by taking the following
precautions:
• Open windows frequently when the weather is dry to allow an exchange of air and permit the introduction of sunlight
throughout your Unit. Even in winter, cracking your windows after showers or cooking can help mitigate excessive moisture
from getting trapped inside. It may help if you run the fan on your furnace to circulate fresh air through your Unit during
these times.
• In damp or rainy weather conditions, keep windows and doors closed.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 21
• If possible, maintain a temperature of between 55° and 75° Fahrenheit within your Unit at all times.
• Regular cleaning (including dusting, vacuuming, mopping and use of environmentally safe household cleaners) is important
to remove household dirt and debris that mold feeds on. Thoroughly dry any spills on carpeting.
• Periodically clean and dry the walls and floors around the sink, bathtub, shower, toilets, windows and patio doors using a
common household disinfecting cleaner.
• Regularly, wipe down and dry areas where moisture sometimes accumulates, like countertops, windows and windowsills.
• Use any preinstalled bathroom fan when bathing or showering and allow the fan to run until all excess moisture has vented
from the bathroom.
• Use the exhaust fans in your kitchen when cooking or while the dishwasher is running, and allow the fan to run until all
excess moisture has vented from the kitchen.
• Limit houseplants to keep the moisture level in your Unit at a minimum.
• Ensure that your clothes dryer vent is properly connected and clean the lint screen after every use.
• When washing clothes in warm or hot water, make sure condensation does not build up within the washer and dryer closet;
if condensation does accumulate, dry with a fan or towel.
• If you live in a humid climate, a small dehumidifier will help regulate humidity levels in your Unit and create a more
comfortable environment.
• Do not overfill closets or storage areas.
• Do not allow damp or moist stack of clothes or other cloth or paper materials to lie in piles for an extended period of time.
Let us know immediately if you spot any of the following:
o Evidence of a water leak or excessive moisture in your Unit, storage room, garage, or any common area.
o Evidence of mold or mildew-like growth that cannot be removed by simply applying a common household cleaner and
wiping the area.
o Mold or mildew that reappears despite regular cleaning.
o A failure or malfunction with your heating, ventilation or air-conditioning system. Do not close or cover any of the
heating, ventilation or air-conditioning ducts in your Unit.
o Inoperable windows or doors.
Community Recreational Amenities
We offer a wide variety of recreational amenities at our Communities. Below are general policies with respect to these amenities. Some
of the following may not apply to your Community, so only read those sections that relate to the amenities available at your Community.
If you are not sure what those are, please contact the Community Office.
Amenities may change during your time with us, and, at any time, we may need to change our Policies and House Rules. This means we
reserve the right, at our sole discretion, without prior notice, to change the hours of such facilities or to discontinue the Resident's use of
all such facilities. Any such changes or termination of such facilities shall in no way serve to lessen the Resident's obligation under the
rental agreement or lease, including the amount of the monthly rent, nor will this serve as a basis for a Resident's early termination of a
lease.
Use of all recreational amenities are at your own risk. Please make sure you know and understand how to operate all equipment before
using it. If you do not feel comfortable with how to operate something, please look it up. Also, be courteous of your neighbors. If someone
is waiting, please limit use to 30 minutes, this applies to all recreational amenities. And while we generally allow each household to bring
two guests into our various community recreational areas, we may limit guest access at any time to ensure the facilities are available to
our residents. Please be advised that our recreational amenities are not supervised; use of the amenities is at your own risk. To keep
everyone safe, a responsible adult (that means they are paying attention to the people they are with) must accompany persons under
the age of 14 when using any of the pool, fitness center or spa facilities at your Community.
Business Center
Certain Communities have been equipped with business centers for use of their Residents.
• Business center hours are as posted and subject to change.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 22
• No food or beverages are allowed in the business center.
• Please treat the equipment correctly. If assistance is needed regarding operation or for repairs, contact the Community
Office.
With respect to our computers:
• Keep it clean. Do not access icons, system files, chat rooms, newsgroups, list servers or bookmarks, access or print
pornographic material, violate copyright laws or otherwise use the intellectual property of others without permission or
download to disks or other storage or personal devices.
• We do not have any responsibility to monitor or prevent access to any sites that may be objectionable, and we cannot and
do not guarantee that any material available on any computer or any Internet site is current, accurate, inoffensive or suited
to any particular user's purpose. We are not responsible or liable for any damages sustained by you or your guests or
others with respect to the use of the center/area, or any computer located in the center/area.
• All Residents must have on proper attire at all times when using the center. That means shirt and shoes, no swimming
attire, etc.
• Please do not unplug, switch or tamper with any of the cables or computer equipment.
Fitness Center
Some Communities provide a fitness center.
The Community fitness center is reserved for the use of our residents and their guests (but only so long as guest use doesn't interfere
with use of other residents). If it gets crowded, we may ask guests to leave (at our discretion). Guests may be required to be registered
at the Community Office prior to their use of the facilities and sign a waiver.
Hours of operation are posted at the facility and/or the Community Office.
We shall not be held liable for any damages or personal injuries sustained by residents and guests in the use of the fitness center
equipment. If you are unfamiliar with the equipment, please refrain from using it until you have received proper instruction. Residents with
heart or similar conditions are advised not to use the equipment without first consulting their physician. Shirts and shoes are required.
Food, glass and alcoholic beverages are not permitted.
Swimming Pools/Spas
Some of our communities offer a pool, spa or hot tub for your enjoyment. Pool hours are posted at the Community. Please be advised
that the pool may be closed occasionally for your safety, due to severe weather or chemical treatments beyond those that are done on a
daily basis. Also, the heating of pools may vary from community to community and seasonally as well.
For your enjoyment and everyone's safety, we enforce the following policies and rules:
• No diving allowed.
• We reserve the right to regulate the use of the pool.
• A lifeguard is not provided. Swim at your own risk.
• Residents in the pool area may be required to show identification.
• A resident must accompany guests. Also, we may require guests to be registered with the Community Office.
• Swimmers must wear bathing suits or trunks. Cut-offs and street clothes are not permitted. Swimmers wearing attire
deemed offensive by Management may be asked to leave the pool area.
• Chairs, tables, umbrellas and other pool accessories provided by us are for safety and comfort. Please do not remove them
from the pool area.
• To keep the pool operating properly, no foreign objects such as pool furniture, plastic cups or liquids are to be put in the
pool or spa.
• Please remove barrettes, hairpins and jewelry to prevent their loss or damage to the pool equipment.
• Rafts, floats, inner tubes, etc., may not be permitted in pool at Management's discretion. Safety equipment, such as swim
vests and floaties, are always allowed.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 23
• Glass containers and alcoholic beverages are not permitted in or around the pool area. If you see broken glass, let us know
immediately.
• Diapers may not be worn in the pool.
• If you're not feeling well, do not use the pool and spa. That means that if you have diarrhea, steer clear. Once you are
feeling better, however, come back and enjoy the water.
• Bicycles, roller skates and skateboards are prohibited in the pool area.
• Don't tamper with the gates, latches or pool fences. Please report broken gate latches to the Community Office.
• Animals are prohibited in the pool area unless they are required to be there in order to assist a person with a disability.
• Be considerate of others, and keep all volumes (music, voices, etc.) at a level that won't bother other people in the pool
area.
• We are not responsible for accidents in the pool or pool area. Please become familiar with the location of the emergency
phone and safety equipment.
Additional Cautions Regarding Spas
For your own protection, we suggest you observe a 10-minute time limit when in the spa. Anyone pregnant or who has a medical condition
should check with their doctor before using any outdoor spa.
We need to be very clear that you should not, under any circumstances, put soap in the spa. It can clog the filters and make the spa
unusable for several days, and violators will end up paying the repair bill.
Please familiarize yourself with the location of the emergency shut-off button, in case an emergency occurs.
Laundry Rooms
Laundry rooms are common areas, so please be advised that we aren't responsible for damages or loss of clothing and personal items
from the laundry rooms.
Some laundry room guidelines:
• Don't sit or stand on the worktable(s). They are designed for laundry folding and sorting.
• Don't overload the machines – they won't work well, and could break down.
• Please make sure to empty your pockets before washing your clothes.
• Promptly remove clothes at the end of the cycle. Otherwise, someone else may do it for you and your Spiderman underwear
will be the talk of the community.
• When a machine isn't working, please call the phone number listed on the laundry room wall and inform the representative
of the machine number. Please notify the Community Office if the problem persists.
Community Barbecue Grills
Some Communities have common area grills for your use and enjoyment. If you use these facilities, please clean up after yourself. Some
communities require the barbecues to be reserved, especially those that require a propane tank – please check with the Community
Office.
Exercise extreme caution disposing of coals, and don't dispose of them in landscaped areas. Instead, wait 24 hours for the coals to
completely cool and then put them in a garbage receptacle.
Play Areas
• Residents of all ages are prohibited from playing on stairs, in trash receptacle areas, and laundry rooms or in any
potentially dangerous area.
• Please do not mark, write, or paint on buildings, walls, sidewalks or landscaped areas.
• Adults are responsible for the behavior of children.
• Finally, but most importantly, all residents should use caution when driving throughout the Community. Watch
closely for younger residents and their guests at play.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 24
Tennis, Basketball, Racquetball and Other Sport Courts
At Communities where these courts are available, the hours of operation are posted. These rules apply to all courts.
• Community Management reserves the right to regulate the use of all courts. Courts are available on a first-come, first-serve
basis.
• Only athletic shoes may be worn on courts.
• Residents must accompany their guests in or around court areas.
• Residents in court areas may be asked to show identification.
• Glass containers and food are not permitted in or around the court areas.
• Don't tamper with court gates, latches, fences, nets, lights or equipment.
• Keep music and noise at a level that only you and your guests can enjoy.
• We are not responsible for accidents or injury.
Roof Decks/Mezzanines
At Communities where these amenities are available, the hours of operation may be limited. These rules apply to all roof
decks/mezzanines.
• Community Management reserves the right to regulate the use of all roof decks/mezzanines.
• Residents must accompany their guests in or around roof decks/mezzanines areas.
• We are not responsible for accidents or injury.
• Roof decks/mezzanines may be available for rental. Please contact the Community Office for details.
Parking
Parking availability varies from community to community; however, the following applies to all of our Communities. For additional
information regarding parking, please review applicable addenda to your lease. It is really important you read and follow the parking
addendum or else your car could be towed at your cost, especially if a parking permit needs to be displayed and you fail to do so.
• We need to keep things safe, so no double parking, parking in red curb areas or blocking of pedestrian ramps or dumpsters.
Generally, tandem parking is the exception, not the rule, and is only permissible at those Communities where it is specifically
authorized. Please check with the Community Office and follow signs with respect to parking at your Community.
• Handicapped spaces are not assigned to specific Residents, and are available to vehicles bearing handicapped
identification. The Police Department will assess steep fines for vehicles violating laws relating to dedicated handicapped
spaces.
• Obey all parking signs, speed limits, directional instructions or other posted instructions. Any person driving or moving a
vehicle on the premises must hold a current, valid driver’s license.
• Residents are responsible for any vehicles belonging to guests, employees or invitees. We make no guarantees as to the
availability of unassigned or visitor parking.
• To the extent parking is assigned at your Community, we reserve the right in our sole discretion to change your assigned
space at any time and from time to time upon prior written notice.
• We are not responsible for any damage, vandalism or loss that occurs on the grounds. All parking is at the driver’s own
risk.
• The speed limit at the Community is 5 miles per hour.
• Car washing and performing vehicle maintenance is not permitted on the Community or with Community utilities unless a
designated car washing area is provided.
• No motorized vehicle will be operated on sidewalks, walkways or any pedestrian area (unless, of course it is an assistance
device for someone with mobility impairment).
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 25
• Storing motorized vehicles in backyards, inside Units, or on patios or balconies is not allowed.
• Racing, gunning motors, squealing tires and loud radio playing in vehicles are not allowed.
• Current and updated license tags are required at all times.
• Resident shall obtain parking authorization for each vehicle that it owns and intends to park on the Community.
• Vehicles that do not have current parking authorization may be subject to towing at the vehicle owner's expense if they
appear to be: (a) inoperable; (b) abandoned; or (c) not owned by a current Resident.
• Automobiles will be deemed inoperable or abandoned if any one of the following occurs:
• 1) The automobile is not currently registered as evidenced by a license plate sticker or registration
• 2) The vehicle remains in the same parking space for more than two (2) weeks, or;
• 3) The physical condition of the automobile would render it inoperable (e.g. multiple flat tires, etc.).
• Vehicles that do not have current parking authorization will be determined to be not owned by a current Resident.
• Parking violations may be dealt with by towing, loss of parking privileges on the Community or possibly eviction, at our
discretion.
Campers, trailers, trucks, boats and recreational vehicles are prohibited without prior written authorization. Don't park them in areas
reserved for cars.
Garages
If garages are available at your Community, you may inquire at the Community Office about leasing one. Additional rent is often required
to lease a garage, and there's a security deposit for a garage door opener (the security deposit is refunded upon return of the garage door
opener).
Additional monthly rent and security deposits do not limit your liability for property damages, cleaning replacements, or personal injury.
If you use a garage, here are some basic guidelines and rules:
• Garages are for vehicle parking only. Storing of personal items other than vehicles, or any flammable liquids in your garage
is prohibited.
Electronic Vehicle Charging Stations
At some Communities we have electric vehicle charging stations (EVCS) available for use by our Residents. You may only park in the
space designated for using the EVCS while actually charging your vehicle (your electric vehicle). If you are parking there when not
charging your car, you may be towed (and the expense for towing is on you). You also need to pay for the use of the EVCS. Only charge
your vehicles at charging stations where available.
Use of the EVCS is subject to Community rules, regulations, posted signage and other instructions made available to you by us.
The EVCS is provided to Resident in its "AS-IS," "WHERE-IS" and "WITH ALL DEFECTS" condition. We expressly disclaim all warranties
or representations of any kind, whether express or implied, including, but not limited to, the implied warranties of merchantability, suitability
and fitness for a particular purpose. Landlord makes no warranties or representations that the EVCS will act in any particular way, meet
any requirements or expectations or that the use of the EVCS will be uninterrupted, timely, secure or error-free.
To the greatest extent allowed by law, by using an EVCS, you assume all risk of harm, release and waive all claims against us from and
against all claims relating to the EVCS by you whether the use is authorized or unauthorized, even if caused by the negligence of us.
Pursuant to California Civil Code §1947.6 we will approve written requests of Residents to install, at your cost, an EVCS at a parking
space allotted to you under certain circumstances in California. If you'd like to know more, please contact the Community Office.
Bicycles
Please store bicycles inside your Unit, enclosed patio, balcony storage areas, or bicycle storage area if provided. Do not store bicycles
under stairways. We are not responsible for lost or stolen bicycles.
If a Bike Room is available at your Community, use of the Bike room is at your own risk. We are not responsible for lost or stolen bicycles
stored here either. It is your responsibility to secure bikes with your own lock. Also, do not let anyone else into the bike room, and make
sure the door is secured upon leaving.
For your safety, wear a bicycle helmet. Bicyclists should always yield to pedestrians.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 26
Safety Guidance
Your personal security, and that of your family and guests, is up to you. Regularly taking common-sense precautions can help you develop
the awareness you need to protect yourself, your family and friends, as well as your personal property. We encourage you to consistently
follow the guidelines listed below.
When you are at home:
• Lock your doors and windows.
• Use your deadbolt or night latch.
• Never answer your door unless you know who is there. Use the peephole or window to confirm who is on the other side.
• If you are worried because you have lost a key, contact the Community Office to have the locks changed. While there is a
charge to change the lock, it's better to be safe than sorry.
• Keep emergency telephone numbers (police, fire and emergency medical) near the telephone.
• If you have broken locks, latches, doors, windows or smoke detectors, contact the Community Office immediately with a
repair request.
• Let the Community Office and trusted neighbors know if you are going to be gone for an extended period of time. While
neither can assume responsibility if a problem occurs, their increased awareness may play a role in prevention.
When you are away from your Unit:
• Lock your doors and remember to use the deadbolts.
• Immediately report malfunctioning gate locks, or dark stairwells and parking areas.
• Close and lock your windows and sliding patio or balcony doors.
• Don't hide your front door key under the doormat.
• If you have an entry code, don't give it to anyone.
When you are driving and parking your car:
• Lock your car doors and never leave your parked car until the doors are locked and the windows are completely rolled up.
• Don't leave garage remotes, gate fobs or your keys in the car.
• Don't leave valuables in your car.
• Check the back seat before you get into the car.
Solicitation
Solicitation is prohibited in the Community. Except as prohibited by applicable law, soliciting of any kind by Resident, Resident's guests
or Resident's invitees is a material violation of this Agreement. If Resident is contacted by a solicitor, even if that person resides at the
Community, please contact Landlord immediately.
Access Gates
Some Communities are furnished with electronically controlled access gates.
Access gates are designed to open with an access gate card or remote control device. The Community Office will provide you with a card
or remote, and will demonstrate how to use it to open the access gate. If you lose an access device, you will need to pay the cost to
replace it.
Do NOT try to follow someone else through the gate. The gates are timed for one vehicle only and the gate may close on you or your
vehicle if you try follow the car in front of you. Trust us: Waiting the few extra seconds to open the gate with your own access device takes
a lot less time (and money) than repairing your car after a gate closes on it. Although the access gates contribute to the peace of mind of
our residents, they are not security and, the presence of the gates does not guarantee that crime can or will be prevented. In particular,
please be aware that non-residents may attempt entry by closely following a resident who is entering the Community. In addition to
allowing unauthorized visitors entry to the Community, this practice can damage the trailing vehicle and compromise the function of the
access gate.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 27
Because We Care, Please Remember...
A fail-safe system or device just doesn't exist. Safety devices such as alarm systems, courtesy patrols, patrol cars, and access gates are
not guarantees against crime. All systems are subject to personnel absenteeism, human error, mechanical malfunctions and tampering.
In the end, your safety is your business, and we urge you to plan and take action as if safety systems and devices didn't exist. Don't
depend on outside systems for security – the best safety measures you can take are the common-sense ones you carry out yourself.
Leaving Us?
If your needs change and you need to relocate, please let us help you find another Community. We have quite a lot of options and will
make it easy for you. Speaking of easy, here are some guidelines for you to make the process of leaving your current Community as easy
as possible.
Let Us Know
As stated in your lease, you need to let us know, in writing, at least 30 days in advance of your anticipated departure date.
Preparing for Your Move-Out
We want your last few days with us to be as smooth as possible. We ask that you return your Unit to us at the same level of cleanliness
as it was when you moved in. That said, here are some helpful tips;
• Cleaning includes flooring, too! It was new or freshly steam-cleaned when you moved in so make sure to give it a good
vacuum and wipe-down. If you don't want to hassle with scheduling a company to steam-clean your carpets before you
move out, check with the Community Office for pricing of a professional carpet clean. We can simply deduct this amount
from your deposit (or send you a bill) for this as well.
Take a look at our cleaning checklist to make sure you have everything covered.
• Your Community Office can provide pricing for a professional cleaner which can be deducted from your security deposit or
billed to you upon move out.
• Remember to let the post office know you're moving. Visit www.usps.com for more details.
• Although you have told us you are moving, it is not official until you return all keys to us. You can return your keys to the
Community Office during business hours or after business hours at properties offering after-hours drop box. Please place
them in an envelope labeled with your name and unit number.
Cleaning and Repairs
The following are our internal guidelines and estimates regarding the costs for cleaning and any necessary repairs. We will evaluate each
Unit on a case-by-case basis, but this will give you some idea of what to expect if you are not able to return the Unit to us in the same
condition you received it (reasonable wear and tear excepted, of course).
If, prior to moving out, you're unable to clean the Unit to the same level of cleanliness as received and leave it in the condition presented
on move-in (normal wear and tear excepted), or if additional service is required or items missing or damaged to the point that they must
be replaced when you move out, you will be charged for the current cost to repair, clean and/or replace, including labor and service
charges. If your security deposit is insufficient to cover the charges, the amount will be billed to you directly.
Moving can be stressful and hectic, so we've provided a list of areas you should clean before departing. Although this is not a complete
list, we hope it will help maximize the amount of your returned security deposit.
Tub, showers and toilet: A tub cleaner should work on most dirt, stains and mildew, as well as rings, bottle marks and soap buildup.
A non-abrasive cleanser and scrub brush can tackle heavier dirt. Make sure the shower doors and soap dishes are clean as well.
Both the interior and exterior of your toilet should be clean, with no marks or discoloration.
Countertop, mirror, sinks and faucets: Ensure these surfaces are free of water spots, rings, smears, residue or dirt.
Stove: Clean under the stovetop and drip pans, which you can lift out by pulling on the burner (please make sure the stove top and
oven are cool first). See if the oven door and top are harboring burnt-on food. Check the exhaust fan above the oven for grease, too.
Microwave: Look under the glass plate for food particles or drips. The interior and door need to be free of stuck-on food, drips,
splatters and discolorations.
Refrigerator and dishwasher: Clean any stains or spills from both the interior and exterior of your dishwasher and refrigerator. You
may need to remove the refrigerator shelves/drawers and clean separately.
Washer/Dryer: Check the interior and detergent/bleach reservoir for any detergent stains. Your dryer may be dusty, so clean out the
interior and lint trap.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 28
Garage, carport, storage closet and patio: Complete sweep and clean. We will need an estimate from our cleaners for any heavy
stains or discoloration.
Walls: Remove all screws and nails, and carefully fill the holes with spackle. You can clean most scuffs with a melamine sponge. If
spot-painting is not sufficient to restore the condition of the walls, we may need to charge you for a full repaint (prorated based on
an amortized period of 3 years).
Floors: All flooring should be free of any spots, stains or fraying not noted on your move-in inspection. Please note that dirty flooring
is not considered normal wear and tear. We do not recommend using your own carpet cleaning machine, which can cause damage
by oversaturating the carpet and leaving detergent residue behind. An ideal option is to contact us and arrange a carpet clean with
our contracted carpet cleaning provider. We'll deduct the fee from your deposit and save you the hassle.
• Clean any drawers and closets and remove all liners.
• Dust all the ceiling fixtures, including ceiling fans - they can harbor a lot of dirt.
• Clean windows, sills and blinds.
• Clean all door knobs and doors, including your front and patio doors.
• Clean all light switches and outlets.
• Replace any burned out lightbulbs.
• Vacuum the exterior of exhaust fans, air ducts and air returns if they are dusty.
We strongly suggest that you request a pre-move-out inspection and be present for the move-out inspection, which are your
opportunities to review the condition of the Unit and any charges with us.
Cleaning and Repair Estimates
Please keep in mind that these are estimates only and that every case is different. If we do have to assess charges, you will be charged
the actual cost of repairs; the following prices are estimates only. If we incur a higher cost for replacing an item, you will be responsible
for paying the higher cost. Please note that this is not an all-inclusive list, and you may be charged for the replacement of items not on
the list. Unless otherwise indicated, costs are per item.
Unit clean Carpet clean † Painting by vendor Painting by Essex
Unit clean Carpet clean† Painting by vendor Painting by Essex
Studio $110-$150 $60-$120 $110-$535 $16-$35/hr
1-bdrm $110-$270 $60-$150 $120-$1250 $16-$35/hr
2-bdrm $120-$310 $70-$200 $170-$1740 $16-$35/hr
3-bdrm $140-$360 $75-$250 $219-$1975 $16-$35/hr
Patio Glass Door $150-$800** Haul Trash $16-$35/hr Vertical Blind Cleaning $30 each
Countertop Refinishing $200-$500** Window Screen $15-$25 Tile $5-$10
Doors $40-$375 Broiler Pan Set $35 Towel Rack $10-$20
Garage Door $200-$500 Fumigation $50-$100 Lightbulb $2-$25
Window Glass $75-$300** Wood Floor Slats $10.75 sqft** Contact Paper Removal $16-$35/hr
Drip Pan Ring $2-$10 Mini Blinds $5-$76 Mirror $50-$350
Door Lock Set $35-$80 Refrigerator Shelf $25-$40 Fire Extinguisher $50-$75
Garage Cleaning $50-$100 Shower Rod $5-$20 Smoke Detector $35
Patio Screen $35-$75 Vertical Blinds $25-$60 Ceiling Fan $75-$100
Key/Opener $25-$150*** Ice Tray $2-$10
Light Fixture $75-$100 Shower Door $150-$350
**Specialty items exceed replacement costs estimates.
***Refer to Access Cards, Keys, Remotes, Directories, and Lock Out Policy Addendum and/or SmartRent Addendum for
details.
General Labor/Cleaning:
General cleaning and other services will be assessed at $16-$35 per hour, including but not limited to labor for trash removal, washing of
walls, doors, doorframes, switch plates, shelving, heat registers, removing contact paper, cork, mirrors, hooks, wallpaper and any other
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 29
miscellaneous cleaning or repair services, other than that required to remedy damage caused by ordinary wear and tear.
Damages or cleaning due to smoke from any source, including cigarettes, shall not be considered normal wear and tear. If damages and
cleaning are necessary due to smoke, you are responsible for charges including sealing of walls or floors and extra cleaning and painting.
Carpet and Vinyl Flooring
Carpet and vinyl flooring are expected to last for 5 years. If we determine that it is necessary to repair or replace the carpet or vinyl flooring
at the end of your tenancy, other than to remedy ordinary wear and tear, you will be charged the cost of repair or replacement. Due to
the inability to color match new and existing carpeting and vinyl flooring, it is often necessary to replace throughout the Unit even if stains
or other defective conditions are not present in every room, and you will be responsible for payment of the cost of the entire replacement,
less any depreciation.
6 months 90% of cost 30 months 50% of cost 54 months 10% of cost
12 months 80% of cost 36 months 40% of cost 60 months 0% of cost
18 months 70% of cost 42 months 30% of cost
24 months 60% of cost 48 months 20% of cost
Pet Damage
If we detect possible pet urine in your Unit, charges may be incurred for pet urine detection, which typically ranges from
$50-$100 per Unit as well as subfloor sealing, which typically ranges from $50 to $350 depending on the size of the Unit and the areas
to be sealed.
Paint
Paint is expected to last for 3 years. If we determine it is reasonably necessary to paint all or part of the rental premises at the end of your
tenancy, other than to remedy ordinary wear and tear, you will be charged the cost, based upon your length of residency.
Acknowledgement
As stated at the outset, the policies and house rules outlined above in the Community Handbook are terms of your Lease and will be
enforced as such. By signing below, you acknowledge that you have received and read the Handbook and you agree to comply with all
of the policies and house rules contained within it.
NOTE: This acknowledgement becomes part of your Lease. This is a binding Legal Document. Read it carefully before signing.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 30
PARKING AGREEMENT
This Parking Agreement ("Agreement") is entered into on 07/31/2025 by and between Essex Management Corporation, a California
Corporation, as agent for Owner of the Community ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma,
Mathesh Thirumalai (individually and collectively referred to herein as "Resident"). Resident has rented from Landlord the premises
located at 145 Chestnut Street #121, Santa Cruz, CA 95060 ("Premises" or "Unit") within the community commonly known as Chestnut
Street (the "Community" or "Property") pursuant to the lease agreement dated 8/25/2025 (the "Lease"). Landlord and Resident agree as
follows:
1. Resident hereby acknowledges that this Agreement is separate from, and independent of, the Lease and does not constitute a
housing service offered to Resident pursuant to the Lease.
2. Resident must be a current tenant in material compliance with Resident’s Lease including, but not limited to, current on all amounts
due and payable under the Lease in order to enter into this Agreement and continue to use Resident’s Parking Space. If Resident(s)'s
tenancy at the Property ends for any reason, Resident(s) and Landlord agree to mutually terminate this Parking Agreement as of
the date of the agreed-upon, court-ordered, or noticed termination of the tenancy. If Resident is not in material compliance with
Resident’s Lease and/or this Agreement, Resident acknowledges and agrees that Landlord may withdraw Resident’s permission to
utilize the Parking Space until such time that Resident cures the breach of Resident’s Lease and/or this Agreement (“Suspension
Period”).
3. Resident acknowledges the accuracy of the information provided below and agrees not to have any vehicles on the Property other
than those below. Resident shall notify Landlord within three calendar days of any changes to the below information.
VEHICLE #1 INFORMATION
EFFECTIVE DATE
08/25/2025
END DATE MAKE MODEL YEAR COLOR
PLATE STATE PARKING PERMIT # PARKING SPACE TYPE
Assigned Uncovered
PARKING SPACE #
472
PARKING FEE PER MONTH
0.00
VEHICLE #2 INFORMATION
EFFECTIVE DATE END DATE MAKE MODEL YEAR COLOR
PLATE STATE PARKING PERMIT # PARKING SPACE TYPE PARKING SPACE # PARKING FEE PER MONTH
VEHICLE #3 INFORMATION
EFFECTIVE DATE END DATE MAKE MODEL YEAR COLOR
PLATE STATE PARKING PERMIT # PARKING SPACE TYPE PARKING SPACE # PARKING FEE PER MONTH
VEHICLE #4 INFORMATION
EFFECTIVE DATE END DATE MAKE MODEL YEAR COLOR
PLATE STATE PARKING PERMIT # PARKING SPACE TYPE PARKING SPACE # PARKING FEE PER MONTH
VEHICLE #5 INFORMATION
EFFECTIVE DATE END DATE MAKE MODEL YEAR COLOR
PLATE STATE PARKING PERMIT # PARKING SPACE TYPE PARKING SPACE # PARKING FEE PER MONTH
4. Resident shall pay, per month, the sum total of all amounts listed in the above table under “PARKING FEE PER MONTH” (“Parking
Fee”) for use of the Garage, Carport, or Parking Space(s) (collectively “Parking Space”) (“Parking Fee”). The Parking Fee shall be
paid in full, in advance, on or before the first day of each month under the same terms and conditions for the payment of Rent
set forth in the Lease.
5. For each vehicle identified in the chart in Paragraph 3, Resident is permitted to utilize the Parking Space on the Effective Date listed
for such vehicle and shall continue from the first day of the month immediately following on a month-to-month basis until terminated,
excepting any Suspension Period. If the Suspension Period exceeds three consecutive months, this Agreement shall terminate and
the Parking Space will be released.
6. Resident acknowledges that all charges incurred under this Agreement, changes to this Agreement, increases or reduction in
services or fees related to this Agreement are separate from the Lease; however, for the sole convenience of Resident, and not to
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 31
reduce any rights of Landlord under this Agreement, Resident may make payments owed under this Agreement concurrently or
combined with rental payments for the above-referenced Premises as defined in the Lease.
7. Landlord and Resident agree that the actual cost to Landlord when Resident pays by a check which is subsequently dishonored by
the bank is difficult or impossible to ascertain, but the Parties agree that Landlord does, in the event of a dishonored check, incur
certain costs, such as additional bookkeeping and administrative charges, bank charges, lost opportunity cost of the late payment,
etc. The Parties accordingly agree that, any time the Landlord does not receive payment due to Resident's check being dishonored,
or returned for Non-Sufficient Funds (NSF), Resident agrees to pay a charge of $25 for the first dishonored check and $35 for any
subsequent dishonored check. Both parties agree that the payment of these sums does not constitute a license to pay by dishonored
check.
8. If a parking permit is required and it was lost or stolen, contact chestnut@essex.com for the replacement cost. Temporary permits
will NOT be issued. The lost and/or stolen permit must be returned to a Community employee if found. The lost and/or stolen
permit number will be invalid and any vehicle displaying it subject to tow.
9. The Parking Space shall be for the use of Resident's vehicle(s) only. No subleasing, assignment, or licensing of space allowed.
10. Resident accepts the Parking Space as being in good condition and will pay Landlord for repairs, cleaning, and removal of refuse
necessary due to negligence or misuse while under Resident's control. At the termination of this Agreement, the Parking Space will
be left free of any debris, broom swept, and undamaged. Resident is responsible for the costs of repair for all damage to the Parking
Space caused during the term of this Agreement.
11. No improvements or alterations shall be made without the prior written consent of Landlord and Resident agrees to protect the walls
and all fixtures, and not to place any nails, screws or books upon the doors, floors or garage walls. No other locks, keys or security
devices may be added to the garage
12. The Parking Space shall not be used for storage of goods. At no time may Resident maintain within the garage any article dangerous
or detrimental to life of the health of the occupants of the Community, nor may there be stored, kept or handled any straw excelsior,
cotton, paper stock, rags, junk or any other flammable material that may create a fire hazard. The use of any electrical equipment
inside any garage/carport/parking area is strictly prohibited.
13. Resident hereby agrees to comply with all rules and regulations issued by Landlord whether posted at the Premises, contained in
the Community Handbook or set forth in the Lease for the Premises or otherwise issued by Landlord. Resident acknowledges that
the failure to do so may result in the towing of the offending vehicle at the vehicle owner's sole cost and expense and also is a
material breach of the Lease, which may lead to the termination of Resident's tenancy. The parties hereto agree that Landlord may
modify or change any parking rules or regulations at any time upon ten (10) days' written notice.
14. Landlord does not provide any insurance insuring Resident's vehicle or other personal belongings. Landlord has no liability
whatsoever for loss or damage to the Resident's property, whether by fire, theft, vandalism, mysterious disappearance or otherwise
while any vehicles are stored within the Parking Space.
15. Resident will indemnify, hold harmless, and defend Landlord from all claims, demands, actions or causes of
action that are hereinafter made or brought about by others as a result of, or arising out of, Resident's use of
the Parking Space.
16. Any stored vehicles or other items shall be deemed abandoned if not removed within ten (10) days after termination of this
Agreement. Upon such abandonment, Landlord may tow vehicle or have it removed at Resident's sole expense. Any personal
property left will be disposed of in accordance with applicable law.
17. If this Agreement provides for the assignment of a specific assigned Parking Space, then Landlord shall have the right to reassign
the specific space for another assigned space upon ten (10) days' written notice to Resident.
18. If any provision of this Agreement is invalid or unenforceable under applicable law, such provision shall be ineffective to the extent
of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this Agreement. Except as
specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of any conflict between
the terms of this Agreement and the terms of the Lease, the terms of this Agreement shall control.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 32
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 33
RENTER'S INSURANCE ADDENDUM
This Renter's Insurance Requirement Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the lease agreement
dated 8/25/2025 (the "Lease") by and between Essex Management Corporation, as agent for Owner of the Community ("Landlord"), and
Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and collectively referred to herein as
"Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060 ("Premises" or "Unit") within the
community commonly known as Chestnut Street (the "Community" or "Property"). All terms not specifically defined in this Addendum
shall have the same definition as found in the Lease. Landlord and Resident agree as follows:
1. Landlord does not insure Resident's personal property or liability. Property and liability insurance obtained by Landlord is not intended
to protect against loss or damage (for example from burglary, vandalism, fire, smoke, or any other perils) to Resident's personal
property. Similarly, if other persons, the Premises or Property are damaged because of the actions of Resident or Resident's guests,
Resident is financially responsible for the damage.
2. Resident’s purchase of Renters Insurance in the amount identified in paragraph 3 is required. Landlord has partnered with Get
Covered to ensure compliance with this Addendum. Unless Renters Insurance is listed as encouraged above, Resident must go to
Get Covered to submit evidence of a third party policy meeting the requirements of Paragraph 3, below, and/or receive information
on how Resident can obtain Renters Insurance. Resident authorizes Landlord to provide information about Resident’s tenancy
including, but not limited to, Resident’s name, email, address, lease start and lease end date to Get Covered. Resident acknowledges
and agrees that Get Covered will provide information back to Landlord including, but not limited to, evidence relating to Resident’s
compliance with this Addendum.
3. Unless Renter's Insurance is listed as encouraged above, Resident's purchase of renter's insurance is mandatory and the following
provisions will apply:
a. Throughout Resident's tenancy, Resident must maintain a renter's insurance policy, at no cost or expense to Landlord. The
insurance policy must have personal liability coverage of at least the amount $300,000 per occurrence.
b. The policy must include coverage for water damage resulting from or related to Resident’s occupancy and/or use of the
Premises (for example, due to a sink overflowing). Resident must provide evidence satisfactory to Landlord, pursuant to
Paragraph 3(d), that Resident’s policy covers water damage as required by this Paragraph.
c. The policy must be written for a term of at least one year, or the term of the lease, whichever is less. The policy must name
Landlord as an "Interested Party" with the following contact information:
i. Address: Essex: PO Box 660121, Dallas, TX, 75266
ii. Email: Essex@policyverify.io
d. Before the beginning of Resident's tenancy, Resident must deliver to Get Covered certified copy of the insurance policy or
certificates of insurance evidencing the existence and amounts of the required insurance. At least thirty (30) days before the
expiration date of the policy, Resident must furnish to Get Covered evidence of renewal or "an insurance binder" evidencing
renewal.
e. The insurance may be issued by any company of Resident's choosing, provided that the insurance company is licensed or
admitted to transact business in in the state in which the Unit is located, and maintains during the policy term an AM Best
rating of at least A-VII.
f. Resident may not do anything or allow any action that invalidates the policy.
g. Each Resident must maintain a Renters Insurance policy complying with this Paragraph 3; however, it shall be permissible for
multiple Residents to maintain coverage under the same policy with the insurance policy or certificate of insurance naming
each person as an Insured, or Additional Insured. Each Resident added to the Lease must deliver to Get Covered a certified
copy of their insurance policy or certificate of insurance evidencing the existence and amounts of the required insurance at the
time they are added to the Lease.
4. Resident may obtain a Renters Insurance policy through any insurance company, broker, or agent, so long as the insurance company
and policy comply with Paragraph 3. Resident may also purchase a Renters Insurance Policy through Get Covered. Policies available
through Get Covered are provided by QBE Insurance, an independent insurance agency. Landlord will benefit financially from
Resident's purchase of a QBE Insurance policy by receiving a fee from Get Covered. Landlord is neither an agent nor broker of
Resident. To repeat - Resident is not required to purchase a QBE Insurance policy through Get Covered. Resident is free to obtain
Renters Insurance from any insurer meeting the requirements of Paragraph 3, above. Landlord and its agents and representatives
are not insurance advisors, so Resident should seek the advice of an insurance professional regarding Resident’s Renters Insurance
options.
5. If Resident does not (1) submit proof of Resident’s Renters Insurance policy that complies with the requirements in paragraph 3 to
Get Covered OR (2) secure a Renters Insurance policy through Get Covered, Resident will be in breach of this Addendum and the
Lease, and in addition to its other rights and remedies, Landlord will have the right, but not the obligation, to schedule the Unit for
coverage under a Landlord Placed Tenant Liability Insurance Policy (“Master Policy”).
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 34
a. The Master Policy coverage is not personal liability insurance nor Renters Insurance. Landlord makes no warranty or
representation that Master Policy covers the Resident’s personal property (contents) or additional living expenses. Landlord
is the named insured under the Master Policy. The Master Policy covers damage to the Unit and Property for which the
Resident is legally liable. It does not protect Resident as if Resident had purchased personal liability or Renters Insurance
from an insurance agent or insurance company.
b. Coverage under the Master Policy may be more expensive than the cost of required insurance available to the Resident from
another provider. At any time, Resident may contact an agent of their choice for Renters Insurance options to provide the
insurance required under this Addendum.
c. If Landlord schedules the Unit for coverage under the Master Policy, Resident shall pay a monthly fee of $14.39 (“Admin
Fee”), pro rated, representing the administrative costs associated with enrolling the Unit in a master insurance policy,
managing the master policy program, collecting the Admin Fee from Resident, and the cost to Landlord for the Master Policy.
Resident acknowledges that the Admin Fee is subject to change on thirty (30) days’ notice. The Admin Fee is due with
Resident’s Monthly Base Rent, in advance, on or before the 1st of each month, paid in a method identified in the Lease.
d. COVERAGE UNDER THE MASTER POLICY IS NOT MANDATORY AND NOT RECOMMENDED. IT IS HIGHLY
RECOMMENDED THAT RESIDENT INSTEAD PURCHASE REQUIRED INSURANCE FROM AN INSURANCE AGENT OR
INSURANCE COMPANY OF RESIDENT’S CHOICE, SO LONG AS THAT INSURANCE COVERAGE COMPLIES WITH
PARAGRAPH 3. Upon Landlord’s receipt of proof of Resident’s insurance pursuant to paragraph 3 above, coverage
under the Master Policy will be terminated. Landlord’s election to enroll the Unit in the Master Policy will not be
deemed a waiver or cure of Resident’s breach under this Addendum. If Resident fails to obtain the required insurance,
Resident is in breach of this Addendum and the Lease, and Landlord reserves all rights and remedies for that breach,
including termination of Resident’s tenancy, even if Landlord has purchased coverage for the Unit under the Master
Policy.
6. The existence of insurance does not absolve Resident of liability for damages or costs to the Unit and/or Property for which
Resident is responsible pursuant to the Lease. In the event of such damage or costs, Resident is required to provide Landlord with
copies of any other additional insurance policies, including, but not limited to, umbrella insurance policies, that may provide
coverage for the damage. Resident remains fully, financially responsible for any loss or damage caused by Resident and
Residents’ guests.
7. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective
to the extent of such invalidity or unenforceability only, without invalidating or otherwise affecting the remainder of this Addendum
or the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event
of any conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 35
SMARTRENT ADDENDUM
This SMARTRENT Addendum (“Addendum”) is entered into on 07/31/2025 by and between Essex Management Corporation, a California
Corporation of the Community (“Landlord”), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai
(individually and collectively referred to herein as “Resident”). Resident has rented from the Landlord the premises located at 145 Chestnut
Street #121, Santa Cruz, CA 95060 (“Premises” or “Unit”) within the community commonly known as Chestnut Street (the “Community”
or “Property”) pursuant to the lease agreement dated 8/25/2025 (the “Lease”). Landlord and Resident agree as follows:
1. Subject to Landlord’s right to cancel or modify this Addendum at any time, Landlord may provide the following services and
equipment: Smart Thermostat; Smart Door Lock; Smart Leak Detector; Smart Plug; and/or Smart Hub (collectively the
“SmartRent Equipment”).
2. Resident may purchase add-on items and equipment, as offered by SmartRent, at Resident’s expense. This includes, but is not
limited to, Smart Motion Sensors and Smart Light Bulbs. For any additional devices purchased, Resident is solely responsible for
all associated costs, maintenance, and security. If Resident voluntarily elects to use such additional devices, Resident
acknowledge the risks and accept responsibility of any costs incurred from installation or use of these devices. This includes any
harms or limitations imposed on the functionality of the SmartRent Equipment provided by Landlord. Both during tenancy and after
it has ended, any additional SmartRent purchases will be your exclusive property and responsibility.
3. Some features of SmartRent Equipment may be used only by downloading and using the SmartRent mobile application available
for smartphones and smart devices via the Apple App Store for iOS devices and the Google Play Store for Android devices (the
“Mobile App” and together with the SmartRent Equipment, “SmartRent”). Resident’s use of the Mobile App is subject to all terms
and conditions of the license agreement for the Mobile App. More information regarding the terms and conditions of the license
agreement may be found on the corresponding Mobile App websites. Resident acknowledges and agrees that the Mobile App and
the Mobile App websites are not owned, controlled, or managed by Landlord.
4. If Resident is locked out and/or experiencing technical problems regarding the Smart Door Lock, immediately contact SmartRent
and its designated support service for assistance. SmartRent has a 24-hours a day, 365-days a year call center available for all
lock issues, which may be contacted at (844) 479-1555. This telephone number may be updated by SmartRent from time to
time. More information can be found on SmartRent’s mobile application or website, https://smartrent.com/. Landlord may assist
Resident with lockouts at cost for a fee. Landlord is not liable for technical difficulties associated with the SmartRent Equipment.
5. EXCEPT AS PROVIDED IN THIS ADDENDUM, RESIDENT UNDERSTANDS THAT THE SMARTRENT EQUIPMENT IS NOT
SUPERVISED, INSPECTED, PATROLLED, OR MONITORED BY LANDLORD IN ANY WAY. LANDLORD MAKES NO
REPRESENTATIONS, RECOMMENDATIONS, OR WARRANTIES REGARDING PROVIDERS OF SMARTRENT TO WHOM
RESIDENT IS REFERRED BY LANDLORD. RESIDENT USE THE SMARTRENT EQUIPMENT AT RESIDENT’S OWN RISK. TO
THE FULLEST EXTENT PERMITTED UNDER APPLICABLE LAW, LANDLORD IS NOT AND SHALL NOT BECOME LIABLE TO
RESIDENT, AUTHORIZED OCCUPANTS, RESIDENT’S INVITEES, RESIDENT’S GUESTS OR OTHER OCCUPANTS OF THE
PREMISES FOR ANY INJURY, DAMAGE OR LOSS WHICH IS CAUSED AS A RESULT OF ANY PROBLEM, BREACH,
DEFECT, CORRUPTION, ATTACK, VIRUS, INTERFERENCE, HACKING, OR OTHER SECURITY INTRUSION, MALFUNCTION
OR PERFORMANCE FAILURE OF THE SMARTRENT. LANDLORD OR ITS AGENT, CONTRACTORS, EMPLOYEES, OR
REPRESENTATIVES SHALL NOT BE LIABLE IN ANY WAY FOR ANY DISRUPTION IN THE OPERATION OR PERFORMANCE
OF SMARTRENT EQUIPMENT. RESIDENT HEREBY RELEASE LANDLORD AND ITS AGENTS, CONTRACTORS,
EMPLOYEES, AND REPRESENTATIVES OF AND FROM ANY AND ALL LIABILITY IN CONNECTION WITH SMARTRENT.
ANY OTHER PROVISION OF THIS ADDENDUM NOTWITHSTANDING, THE RESIDENT ACKNOWLEDGES AND AGREES
THAT (A) NEITHER LANDLORD NOR ANY PARTY ON BEHALF OF LANDLORD IS MAKING ANY REPRESENTATIONS OR
WARRANTIES WHATSOEVER, EXPRESS OR IMPLIED, BEYOND THOSE EXPRESSLY MADE BY LANDLORD AND
RESIDENT IN THIS ADDENDUM, AND (B) THE RESIDENT HAS NOT BEEN INDUCED BY, OR RELIED UPON, ANY
REPRESENTATIONS, WARRANTIES OR STATEMENTS (WRITTEN OR ORAL), WHETHER EXPRESS OR IMPLIED, MADE
BY LANDLORD, THAT ARE NOT EXPRESSLY SET FORTH IN THIS ADDENDUM.
6. Resident understand that use of the SmartRent features may involve installation of certain equipment in the Premises, and/or
providing certain equipment to Resident. Initial installation is performed with no cost to Resident. If Resident loses, damages, or
destroys any of the SmartRent Equipment, Resident will be responsible for the full replacement and/or repair cost of such
SmartRent Equipment, plus any applicable installation fees. Resident will surrender the SmartRent Equipment provided by
Landlord at the end of the Lease term in as good condition as existed at the beginning of the Lease term, ordinary wear and tear
excepted. Except as otherwise expressly provided herein, Resident will not make any alterations,additions, removals, repairs
or improvements to Landlord’s SmartRent Equipment without Landlord’s prior written consent. If Resident suspects damage to any
SmartRent Equipment, Resident must notify Landlord immediately. If Resident fails to promptly notify Landlord of any problem,
failure, malfunction, defect or other issue with the SmartRent Equipment, then the SmartRent Equipment will be deemed to be in
good condition and working order. Resident agrees not to unplug or otherwise remove or tamper with the SmartRent Equipment,
including the Smart Hub. Resident acknowledges and agrees that unplugging the Smart Hub will compromise the SmartRent
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 36
Equipment’s connectivity, functionality and performance. In addition to any costs associated with the repair or replacement of
damaged or lost SmartRent Equipment, Resident also agrees to reimburse Landlord for any costs incurred to plug in and
reconnect SmartRent Equipment that has been unplugged or removed by Resident, Authorized Occupants, Resident’s Guests,
and/or Resident’s invitees. Further, in the event that a third-party service provider or vendor assists in installing or activating the
SmartRent Equipment and charges a fee for cancelling, rescheduling, or missing an appointment, then Resident is liable for the
full amount of the fee. All SmartRent Equipment used in connection with SmartRent must be approved and/or installed by
Landlord’s maintenance employees or approved vendors.
7. LANDLORD MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND REGARDING SMARTRENT, EXPRESS OR
IMPLIED (INCLUDING THOSE REFERRED TO IN THE UNIFORM COMMERCIAL CODE OR IN ANY STATUTE OR RULE OF
LAW THAT CAN BE LIMITED OR WAIVED OR ANY REPRESENTATION OR WARRANTY THAT WOULD OTHERWISE BE
APPLICABLE TO REAL PROPERTY), AND SMARTRENT SHALL BE DEEMED TO BE “AS IS, WHERE IS,” AND IN ITS THEN
PRESENT CONDITION, AND RESIDENT SHALL RELY UPON ITS OWN EXAMINATION THEREOF. IN ANY EVENT,
LANDLORD MAKES NO WARRANTY OF MERCHANTABILITY, SUITABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR
QUALITY WITH RESPECT TO ANY OF THE SMARTRENT EQUIPMENT, OR AS TO THE CONDITION OR WORKMANSHIP
THEREOF OR THE ABSENCE OF ANY DEFECTS THEREIN, WHETHER LATENT OR PATENT.
8. If any provision of this Addendum is declared or found to be illegal, unenforceable, or void, in whole or in part, then the parties
shall be relieved of all obligations arising under such provision, but only to the extent that it is illegal, unenforceable, or void, it
being the intent and agreement of the parties that this Addendum shall be deemed amended by modifying such provision to the
extent necessary to make it legal and enforceable while preserving its intent or, if that is not possible, by substituting therefor
another provision that is legal and enforceable and achieves the same objectives.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 37
ACCESS CARDS, KEYS, REMOTES, AND LOCK-OUT POLICY
ADDENDUM
This Access Cards, Keys, Remotes, and Lock-Out Policy Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of
the lease agreement dated 8/25/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as agent
for Owner ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and
collectively referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060
("Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All terms not
specifically defined herein shall have the same definition as found in the Lease.
1. The following are the keys, access cards, devices, remotes, etc. (collectively referred to herein as "Access Devices") issued at the
time of move-in are identified below:
Area and Type Number
Mailbox Keys 4
2. Access Devices will not be issued to non-lease holders including, but not limited to minors who occupy the Unit, Resident's cleaning
staff, service staff or child/adult care workers. Properties without access entry keys, fobs and other card systems may be equipped
with a numerical pin code device. If such pin codes are issued, Resident will be given the code at the time of move in. Resident
agrees not to share Access Devices or pin codes with non-residents.
3. Resident understands and agrees that Resident's use of any Access Device may be monitored by Landlord and information as to
Resident's use of an Access Device may be retained and reviewed by Landlord in its sole discretion. Landlord's use of this information
may include, but is not limited to, monitoring use of amenities and investigating theft and/or other damage to an amenity or equipment
contained therein.
4. Resident shall not change or install any special locks requiring an entry key without written consent of Landlord.
5. All Access Devices must be returned upon vacating the Unit.
6. If an Access Device becomes lost, stolen or damaged, or is not returned upon the termination of the tenancy created by the Lease,
Resident agrees to report such loss, theft, or damage to Landlord immediately and pay the replacement fee. The replacement fee is
calculated by Landlord after making a reasonable endeavor to estimate accurately the approximate costs associated with the
replacement of each Access Device. Landlord and Resident agree that the actual cost to Landlord when an Access Device becomes
lost, stolen or damaged, is difficult or impossible to ascertain, but the Parties agree that Landlord does, in the event of a lost, stolen
or damaged Access Device, incur certain costs, such as the cost of replacement, reprogramming, additional record keeping and
similar administrative time. Resident may contact the Management Office to determine the replacement fee for Resident’s Access
Device.
7. If the Property is equipped with an access directory, Resident may designate the name to be displayed so long as the name displayed
is a signatory to the Lease. Long distance telephone numbers are prohibited as directory numbers. In some cases, cellular telephone
numbers may not be used as a directory number. Additional Directory instructions may be included in Resident's move-in package.
8. Landlord may provide a lock-out service subject to a fee during office hours for all authorized occupants of the Unit, including
minors. After hours lockouts are not considered a maintenance emergency. If Resident requires a lock-out service after the
Management Office has closed, Resident should retain the services of a locksmith at Resident’s own cost. Resident is responsible
for taking necessary precautions to see that members of Resident’s household do not lock themselves out of the Unit without a
key. For Residents with SmartRent access devices, please refer to the SmartRent addendum for information regarding
lock outs.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 38
a. If you do not want members of your household asking a staff person to let them into the Unit, please notify Landlord in
writing. If Landlord does not receive written instructions signed by a leaseholder, Landlord will continue to let any member
of your household whose name is listed on the Lease, including minors, into the Unit upon request.
b. Landlord may, but will not be obligated to, require the authorized occupant to provide picture identification acceptable to
Landlord each time that the authorized person seeks access the Premises.
c. Resident understands Landlord will not supervise the authorized person while in the Premises or on the Property.
d. Landlord may discontinue this service at any time, with or without cause. Landlord is not responsible for any damages or
injuries which may occur for either granting or denying access to anyone consistent with this policy.
9. RESIDENT AGREES TO INDEMNIFY, DEFEND AND HOLD HARMLESS THE OWNER OF THE PROPERTY, LANDLORD,
ESSEX PROPERTY TRUST, INC., ESSEX PORTFOLIO MANAGEMENT, L.P., EACH OF THEIR AFFILIATES AND
SUBSIDIARIES AND EACH AND EVERY OFFICER, AGENT, AND EMPLOYEE OF EACH OF THE FOREGOING ENTITIES FOR
ANY LIABILITY OR LOSS OF ANY KIND WHATSOEVER RELATING TO OR RESULTING FROM (1) LANDLORD PROVIDING
ACCESS TO THE PREMISES; AND (2) UNAUTHORIZED USE OF RESIDENT’S ACCESS DEVICE.
10. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective
to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this addendum or
the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of
any conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 39
VALET TRASH AGREEMENT
This Valet Trash Agreement ("Agreement") dated 07/31/2025 is attached to and made a part of the lease agreement dated 8/25/2025
(the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of the Community
("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and collectively
referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060 ("Premises"
or "Unit") within the community commonly known as Vela on Ox (the "Community" or "Property"). All terms not specifically defined in
this Addendum shall have the same definition as found in the Lease. Landlord and Resident agree as follows:
1. Landlord provides to Resident valet trash services. Resident may place trash in a designated container outside
Resident’s door between 6 PM and 8 PM, Sunday through Thursday excluding New Year’s Eve, New Year’s Day, Easter
Sunday, Memorial Day, Fourth of July, Labor Day, Halloween, Thanksgiving Day, Christmas Eve, and Christmas Day. Trash
collection will begin at 8 PM.
2. Resident shall pay to Landlord $50 (“Valet Fee”) per month for valet trash services. The Valet Fee shall be paid in full,
in advance, on or before the first day of each month under the same terms and conditions for the payment of Rent set forth in
the Lease. Resident acknowledges that all charges incurred under this Agreement, changes to this Agreement, increases or
reduction in services or fees related to this Agreement are separate from the Lease; however, for the sole convenience of
Resident, and not to reduce any rights of Landlord under this Agreement, Resident may make payments owed under this
Agreement concurrently or combined with rental payments for the Premises.
3. If Resident misses service on any of the designated nights, it is Resident’s responsibility to bring trash to the trash room
or dumpster. Resident may not leave trash in the hallway except during the designated times listed above. Landlord reserves
the right to modify or terminate the valet trash services upon 30 days written notice to Resident. If Resident damages the trash
container requiring replacement, Resident agrees to pay Landlord $25 (“Replacement Fee”). Resident agrees to the comply
with the following rules and such additional rules relating to the valet trash service as Landlord may set from time to time in
Landlord’s sole discretion:
a. Bag and securely tie all waste;
b. Double bag any items that may leak;
c. To use bags that securely hold contents without ripping or leaking;
d. Resident will not include needles or other sharp objects;
e. Resident will break down all carboard boxes as well as bundle newspapers and magazines;
f. Resident will bring the designated container back into the Premises no later than 9 AM the morning following collection.
4. Resident agrees to indemnify, defend and hold harmless the Owner of the Property, Landlord, and each of their parents,
affiliates, and subsidiaries, and each and every officer, agent, and employee of each of the foregoing entities from and against
any claims arising out of or relating to Resident’s use of the valet trash services.
5. The parties agree a breach of this Utilities Addendum is a material breach of the Lease thus entitling Landlord to the
same remedies under the Lease. Landlord may also terminate specific services.
6. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall
be ineffective to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder
of this addendum or the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain
unchanged. In the event of any conflict between the terms of this Addendum and the terms of the Lease, the terms of this
Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 40
UTILITIES ADDENDUM
This Utilities Addendum ("Utilities Addendum") dated 07/31/2025 is attached to and made a part of the License Agreement dated
8/25/2025 (the "License") by and between Essex Management Corporation, a California Corporation as agent for Owner ("Employer"),
and Haardhik Mudagere Anil, ("Employee") for the use of the premises located at 145 Chestnut Street #121, Santa Cruz, CA, 95060
Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All terms not specifically
defined herein shall have the same definition as found in the License. Employee and Employer agree as follows:
1. General: Employee’s monthly License Fee under the License does not include charges for any utilities. Employee is responsible for
the costs of all utilities identified on Exhibit A to this Utilities Addendum. Employees may be charged for utilities in two ways: Direct-
Bill Utilities and Allocated Utilities.
2. Direct-Bill Utilities: For the "Direct-Bill Utilities" identified on Exhibit A, Employee is required to set up service with the utility provider
and be billed directly from the utility provider as the Customer of Record. Service must be established as of the License start date in
Employee's name by contracting directly with the utility provider and failure to do so may result in an interruption of services and is
considered a material breach of the License. Employer and Employee agree that if Employee fails to establish service in Employee's
own name, Employer or Billing Provider will incur certain costs (e.g., additional bookkeeping, administrative time, and lost opportunity
costs) that will be difficult or impossible to ascertain. Employer and Employee agree that the amount set forth in Exhibit A is a fair
estimate of the damages Employer will suffer as a result of Employee's failure. Employee must terminate Direct Billed Utility service
provided in their name when Employee vacates the Premises.
3. Allocated Utilities
a) The other utilities for which Employee is responsible are referred to herein as "Allocated Utilities." Employee agrees to pay to
Employer, in addition to the License Fee, all Allocated Utilities during the term of the License. For the Allocated Utilities,
Employee shall pay a monthly amount stated in a separate bill ("Allocated Utility Bill") sent to Employee by Employer or a third
party billing service provider ("Billing Provider") for the Property. Payment of the Allocated Utility Bill is due as noted on each
Allocated Utility Bill. Unless otherwise provided, Employee agrees to pay the Allocated Utility Bill monthly at the location identified
on such Allocated Utility Bill.
b) Employee agrees that Employer may bill for additional utilities and services, at which time such additional utilities and services
shall for all purposes be included in the term "Allocated Utilities," as well as change the Billing Provider, the method of billing
and/or the method of allocation with thirty (30) days' written notice to Employee.
c) Charges for Allocated Utilities (if any) will itemize the beginning and ending meter readings, the rate charged to Employee and
any other information required by applicable law, rules or regulations. Billing amounts will be determined by multiplying the sub-
meter readings for the Employee's Premises by the effective utility rate that is charged to Employer. The effective rate is
calculated by adding together all charges from the utility provider, including base fees, miscellaneous charges, fees and taxes
contained on the utility bills divided by the total consumption. Employee agrees to allow Employer, or the Billing Provider, access
to Employee's Premises in order to install, repair, remove and/or read sub-meters. To the extent permitted by applicable law,
the Billing Provider may estimate Employee's sub-meter consumption of Allocated Utilities if Employee's sub-meter is broken, a
meter cannot be read, does not transmit a meter reading or upon move-in or move-out.
d) Employee's Allocated Utilities may be estimated if Employer or Billing Provider has not received bills from utility providers in time
to prepare Employee's Allocated Utility Bill.
e) The allocation formulas set forth in Exhibit A will calculate Employee's share of the Allocated Utilities and all costs of providing
same in accordance with state and local law. Under any allocation method, Employee may be paying for utility usage in common
areas or in other residential units as well as administrative fees or other charges imposed by the utility provider. Both Employer
and Employee agree that using the allocation formula set forth herein as a basis for allocating utility costs is fair and reasonable,
while recognizing that the allocation method does not reflect actual utility consumption by Employee.
f) For Allocated Utilities, all charges assessed to Employer from the utility providers or on property tax bills may be used to calculate
the amount charged to Employee under the allocation formula. Such charges may include, but are not limited to, usage charges,
miscellaneous charges, fees, taxes, drought or other surcharges, fines or other penalties. Allocated charges for Trash may
include all costs incurred by Employer relating to Trash, including, but not limited to charges from the hauler for removing the
trash and recycling, porter service, bulky item removal, cleaning of the bins and deodorizing services, third party vendor contracts
providing services relating to trash and recycling as well as composting costs where required.
4. Common Area Deduction ("CAD"): If indicated in Exhibit A, a CAD is deducted from the sum of the Employer's utility bills for the
utility indicated and relates to the expense of such utility associated with any common areas such as laundry facilities, irrigation,
pools, fountains, etc. Employer and Employee agree that the exact amount of utilities consumed in the common areas cannot be
determined precisely; therefore, the CAD indicated is a fair and reasonable estimate of the usage in common areas even though the
utilities are not separately metered. Employer will deduct the percentage of CAD identified in Exhibit A from the sum of the Employer's
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 41
utility bills for the utility indicated each month before allocation of such bills to Employee according to the allocation formulas
described. The percentage CAD deduction may be changed by Employer with thirty (30) days' written notice by Employer to
Employee.
5. Default in Payment of Allocated Utility Bills
a) To the extent permitted by law, any delinquent payment of an Allocated Utility Bill shall be considered a default under the License
to the same extent and remedies as if Employee had been delinquent in Employee's payment of the monthly License Fee.
b) Employer and Employee agree that when Employee fails to pay Allocated Utility Bills on time, Employer may apply monthly
License Fee to the overdue Utility Bill. If Employee fails to pay Allocated Utility Bills on time, or when Employee pays by a
dishonored check, the actual cost to Employer and/or Billing Provider is difficult or impossible to ascertain, but Employer and
Employee agree that Employer and/or Billing Provider does, in the event of late payment or in the event of a dishonored check,
incur certain costs, such as additional bookkeeping and administrative time, bank charges, lost opportunity costs of the late
payment, etc. After making a reasonable endeavor to estimate accurately the approximate costs associated with a non-payment
of the Allocated Utility Bill, Employer and Employee agree that the amount set forth in Exhibit A is a fair estimate of the damages
Employer will suffer as a result of the late payment. The parties further agree that an NSF fee of $25, plus the payment required
to replace the dishonored check, is a fair and reasonable amount to compensate Employer in the event Employee's check is
dishonored. The Parties further agree that the payment of these sums does not constitute an agreement to pay Allocated Utility
Bills late and/or to pay by dishonored check.
6. Upon vacating the Premises, a final Allocated Utility Bill will be issued by either the Billing Provider or Employer. The cut-off date for
this final bill will be the date that Employee surrenders possession of the Premises to Employer. To the extent permitted by law,
Employee acknowledges and agrees that any unpaid Allocated Utility Bill, together with the amount of the final bill, may be deducted
from the security deposit, in addition to the License Fee, at the termination of the License.
7. Employer is not liable for any losses or damages Employee incurs as the result of outages, interruptions, or fluctuations in utilities
provided to the Premises and waives any claims against Employer for offset, except if the direct result of the sole negligence of
Employer.
8. Employee agrees not to terminate, cut off, interrupt or interfere with any system supplying utility services to the Premises and shall
not disturb, tamper, adjust, or disconnect any utility service sub-metering device. Employee shall not intentionally utilize utilities of
another unit whether or not such unit is occupied. Employee shall not breach any cable or satellite dish system, but will instead
contract with appropriate parties for use of such services.
9. Employee agrees to comply with any utility conservation efforts implemented by Employer and abide by all applicable laws and
ordinances pertaining to utilities. Employee further agrees to reimburse and indemnify Employer for all fines or other penalties
incurred by Employer as a result of Employee's violation of any statute, ordinance, regulation or other governmental restriction.
10. If any utilities listed in this Utilities Addendum are separately billed or metered to Employee, then Employee hereby grants
permission for the release by such utility service providers to the Employer of any and all of Employee’s energy usage data and
related information (“Energy Usage Data”). Employer shall use Energy Usage Data only (i) to monitor or improve the environmental
performance of the Premises and/or Community, (ii) measure the environmental performance of the Premises and/or Community
against performance targets; or (iii) report on the environmental performance of the Premises or Community. To the extent Employer
discloses the Energy Usage Data to third parties, it shall not identify Employee. Employer and Employee agree such disclosure
may include, at most, Employee’s unit number.
11. Employer may modify the method by which utilities are furnished to Employee's unit and/or billed to Employee during the term of the
License. This includes, but is not limited to, sub-metering the unit for certain utility services and/or changing the allocation formula.
Such changes may also include changing the CAD percentage and/or changing flat-rate amounts. In the event Employer chooses to
modify the method or allocation formula used to calculate charges for utility services, Employer will provide Employee at least thirty
(30) days' prior written notice of such modification.
12. Any provision specifically required by applicable law which is not included in this Utilities Addendum is hereby inserted as an
additional provision of this Utilities Addendum, but only to the extent required by applicable law and then only so long as the provision
of the applicable law is not repealed or held invalid by a court of competent jurisdiction.
13. If any provision of this Utilities Addendum or the License is invalid or unenforceable under applicable law, such provision shall be
ineffective to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this
addendum or the License. Except as specifically stated herein, all other terms and conditions of the License shall remain unchanged.
In the event of any conflict between the terms of this Utilities Addendum and the terms of the License, the terms of this Utilities
Addendum shall control.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 42
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 43
EXHIBIT A TO UTILITIES ADDENDUM
1. Employee's billing statement will include a monthly service charge of no more than $6. The service charge represents the reasonable
value of services provided by Employer and/or the Billing Provider to allocate the utility costs, provide billing to Employee, process
payments and, where applicable, postage costs. The monthly service charge is subject to change upon thirty (30) days' written notice.
In any jurisdiction where such charges are prohibited for one or more specific utility, the monthly service charge does not include any
costs for preparing bills or other services relative to those specific utilities.
2. As set forth in this Utilities Addendum, a late fee of $0 may be imposed anytime Employee fails to pay an Allocated Utility Bill by the
due date set forth in the Allocated Utility Bill.
3. As set forth in this Utilities Addendum, a fee of $50 may be imposed each month (or part thereof) that a Employee fails to put a Direct
Bill Utility into Employee's own name.
4. While Employer reserves the right to change who prepares Allocated Utility Bills at the Property, at the time of execution of this
Utilities Addendum, Allocated Utility Bills are provided to Employee by:
a) A Third Party Billing Provider, which, as of the execution of this Utilities Addendum is Conservice. The Third Party Billing
Provider may be contacted with any questions or concerns regarding their billing any time between 5:00 A.M. and 7:00 P.M
MT at (866) 947-7379, via letter to P.O. Box 4718, Logan, UT 84323, or email at service@conservice.com.
5. Explanation of Terms and Formulas
a) "50/50" means the charges to Employee are allocated based on 50% occupancy (number of Employees and authorized
occupants in the Premises as a percentage of all the residents at the Property at a given point in time, usually monthly) and 50%
of the square footage of the Premises as a percentage of all occupied square footage at the Property.
b) To determine the occupancy portion of the allocation, Billing Provider or Employer will divide the charges being allocated in half
after applying the CAD and then divide the result by the total occupant usage factor. Billing Provider will calculate Employee's
share by multiplying the result of this calculation by the occupancy factor based upon the total number of authorized occupants
in Employee's Premises. Because two people do not use twice as much of a utility as one person due to shared usage, the
following occupancy factor is used to reflect an estimate of consumption. The occupancy factor is determined by the following:
Number of Occupants Occupancy Factor
1 1
2 1.6
3 2.2
4 2.6
5 3
6 3.4
i. To determine the square footage portion of the allocation, Billing Provider will take the remaining charges to be allocated
and divide it by the total occupied square feet and then multiply the result of this calculation by the estimated square footage
of Employee's Premises.
ii. The amounts resulting from the above-calculations are added together to determine Employee's allocated share of the utility
charges and will be reflected on Employee's Allocated Utility Bill.
c) "100% Occupancy" allocation means, after deducting the CAD, Billing Provider divides the charges being allocated by the total
occupant usage factor of the authorized occupants at the Property. Billing Provider calculates Employee's share by multiplying
the result of this calculation by the occupancy factor based upon the total number of authorized occupants in the Premises.
d) “100% Square Footage" allocation means, after deducting the CAD, Billing Provider divides the charges being allocated by the
total square feet of all occupied square footage. Billing Provider will then multiply the result of this calculation by the estimated
square footage of Employee's Premises.
e) "By Unit" means the total charges being allocated, after deducting the CAD is divided by the total number of units at the Property
and the result is Employee's allocation.
f) "Not to Exceed Amount." If the Property is in a rent-controlled jurisdiction, Employer and Employee understand and acknowledge
that, for purposes of the applicable rent control ordinance, all utilities charges required to be paid by Employee under the Utilities
Addendum are considered a portion of the License Fee paid for the Premises and shall be considered as part of the License
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 44
Fee when calculating allowable increases under the rent control ordinance. The maximum utility fee to be billed to Employee by
or on behalf of Employer (as opposed to any Direct-Bill Utilities) shall be the amount calculated by adding together all of the "not
to exceed" amounts for utilities for which Employees are responsible according to the above table as well as any monthly billing
or service fees required under the Utility Addendum, if applicable. The fee related to these utilities and services actually billed to
Employee may be less than the "not to exceed" amounts in order to reward overall conservation efforts and to pass on to
Employee decreases in rates from the utility providers.
g) "Flat Rate" charges are set by Employer and may or may not be based on a specific formula.
h) For sewer charges when the "Water Usage" box is checked, allocation is based upon the sub-metered usage of water.
Employee's share of the sewer utility charges to Employer shall be calculated by taking the amount of sub-metered water usage
and multiplying it by the effective rate for sewer charged by the utility provider. For additional information regarding sub-meter
calculations, please refer back to the Utility Addendum paragraph related to charges for allocated utilities based on sub-meter
readings.
i) "Hot Water Energy" means energy used in a central water heating system at the Property to heat water which is then supplied
to the Employee's premises for hot water and/or heat.
6. UTILITIES FOR THE PREMISES SHALL BE CHARGED AS DESCRIBED IN THE BELOW:
a) Employees of the remaining units in the Community shall be charged as follows:
Utility/Service Utility’s Customer of
Record
Calculation Method
for Utility Charge to
Employee
Allocation Formula;
Flat Rate Amount;
Not to Exceed
Amount
Common Area
Deduction
Gas Resident Direct billing from utility N/A N/A
Electricity Resident Direct billing from utility N/A N/A
Water Resident Direct billing from utility N/A 0%
Sewer Resident Direct billing from utility N/A 0%
Cable /
Satellite Dish
Resident Direct billing from utility N/A N/A
Phone Resident Direct billing from utility N/A N/A
Internet Resident Direct billing from utility N/A N/A
Trash Landlord Allocation formula
Flat Fee:
1 bed $25
2 bed $50
0%
Hot Water
Energy N/A N/A N/A N/A
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 45
MOLD ADDENDUM
This Mold Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the lease agreement dated 8/25/2025 (the
"Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of the Community ("Landlord"),
and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and collectively referred to herein
as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060 ("Premises" or "Unit") within
the community commonly known as Chestnut Street (the "Community" or "Property"). All terms not specifically defined in this Addendum
shall have the same definition as found in the Lease. Landlord and Resident agree as follows:
1. Mold consists of naturally occurring microscopic organisms. Mold breaks down and feeds on organic matter in the environment.
When moldy materials are damaged or disturbed, mold spores and other materials may be released in the air. Exposure can occur
through inhalation or direct contact. Most molds are not harmful to most people, but it is believed that certain types and amounts of
mold may lead to adverse health effects in some people. In order to prevent organic growth within the Premises, Resident specifically
agrees to:
a. KEEP THE PREMISES CLEAN:
• Maintain good housekeeping practices and regularly dust, vacuum and mop to keep the Premises free of dirt and debris
that can contribute to mold growth
• Use household cleaners on hard surfaces
• Remove garbage regularly and remove moldy or rotting items promptly from the Premises (whether food, wet clothing, or
other material)
b. CONTROL MOISTURE IN THE PREMISES AND INCREASE AIR CIRCULATION:
• Use hood vents when cooking
• Use exhaust fans when bathing/showering until moisture is removed from the bathroom
• Hang shower curtain inside the bathtub when showering or securely close shower doors
• Leave bathroom and shower doors open after use
• Use air conditioning, heating and/or fans as necessary to keep air circulating throughout the Property
• Water all indoor plants outside
• Close windows and doors (when appropriate) to prevent rain and other water from coming inside the Premises
• Open windows when appropriate to increase air circulation
• Wipe up visible moisture
• If a dryer is installed in the Property, ensure that the vent is properly connected and clear of any obstructions and clean the
lint screen regularly
• Ensure good air circulation in closets, cupboards and shelves by periodically keeping them open, not stacking items tightly,
and/or using products to control moisture
• Regularly empty dehumidifier, if used
c. PERIODICALLY INSPECT THE UNIT FOR MOISTURE AND MOLD:
The most reliable methods for identifying the presence of elevated amounts of mold are (1) smell and (2) routine visual
inspections for mold or signs of moisture and water damage. Resident agrees to conduct an inspection of the Premises (both
visually and by smell) for the presence of mold growth inside the Premises at least once per month. The inspection will include,
but is not limited to:
• Window frames, baseboards, walls and carpets
• The ceiling
• Any currently or formerly damp material made of cellulose (such as wallpaper, books, papers, and newspapers)
• Appliances (including washers/dryers/dishwashers and refrigerators)
• Around all plumbing fixtures (toilets, bathtubs, showers, sinks, and below sinks)
• Areas with limited air circulation such as closets, shelves and cupboards
• Personal property
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 46
d. PROMPTLY REPORT TO LANDLORD IN WRITING:
• Visible or suspected mold that Resident does not clean as explained below. Mold may range in color from orange to green,
brown, and/or black. There is often a musty odor present.
• Overflows or dripping from showers, bath, sink, toilet, washer, refrigerator, air conditioner
• Plumbing problems
• Discoloration of walls, baseboards, doors, window frames, ceilings
• Loose, missing or failing grout or caulk around tubs, showers, sinks, faucets, countertops
• Clothes dryer vent leaks
• Any non-operational windows, doors, fans, heating or air conditioning units
• Any evidence of leaks or excessive moisture in the Premises or on the Property
• Any maintenance needed at the Premises or Property
e. RESIDENT AGREES TO NOT:
• Bring any personal property into the Premises that may contain high levels of mold, especially "soft possessions" such as
couches, chairs, mattresses, and pillows
• Stack items against walls in a manner that decreases air circulation and may lead to mold
• Maintain an excessive number of indoor plants
• Maintain a fish tank or other water filled container without Landlord's written consent
2. If a small amount of mold has grown on a non-porous surface such as ceramic tile, Formica, vinyl flooring, metal, or plastic, and the
mold is not due to an ongoing leak or moisture problem, Resident agrees to clean the area with soap (or detergent) and a small
amount of water, let the surface dry, and then within 24 hours apply a non-staining cleaner such as Lysol Disinfectant, Tilex Mildew
Remover, or Clorox Cleanup. If Resident is unable or unwilling to clean the area, Residents will promptly notify Landlord so that
Landlord can clean area.
3. Resident agrees to defend, indemnify and hold harmless Landlord and Landlord's related parties (past and present
subsidiary corporations, affiliates, successors, assigns officers, directors, property managers, agents, attorneys,
employees and representatives) from claims, liabilities, losses, damages and expenses (including attorneys' fees), that they
incur that are related to the Resident's breach of the Resident's obligations to Landlord. Resident is responsible for the
action (or inaction) of Resident's household members, guests and agents.
4. If elevated mold levels exist at the Premises or Property, Resident agrees to temporarily vacate the Premises to allow for investigation
and remediation, to control water intrusion, or allow other repairs to the Property, if requested by Landlord. Resident agrees to comply
with all instructions and requirements necessary to prepare the Premises for investigation and remediation, to control water intrusion,
to control mold growth, or to make repairs. Storage, cleaning, removal, or replacement of contaminated or potentially contaminated
personal property will be Resident's responsibility unless the elevated mold growth was the result of Landlord's negligence, intentional
wrongdoing or violation of law. Landlord is not responsible for any condition about which Landlord is not aware. Resident agrees to
provide Landlord with copies of all records, documents, sampling data and other material relating to any water leak, excessive
moisture, mold conditions in the Premises as soon as Resident obtains them.
5. Resident hereby acknowledges receiving the attached “Information on Dampness and Mold for Renters in California”.
6. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective to
the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this addendum or the
Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of any
conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 47
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 48
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 49
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 50
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 51
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 52
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 53
PESTICIDE DISCLOSURE
This Pesticide Notice/Disclosure ("Addendum") dated 07/31/2025 is attached to and made a part of the lease agreement dated 8/25/2025
(the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of the Community
("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and collectively
referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060 ("Premises"
or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All terms not specifically defined
in this Addendum shall have the same definition as found in the Lease. Landlord and Resident agree as follows:
1. Resident is informed that pesticides may have been applied to the Unit and/or Property in the past. California law requires that
building owners and operators provide tenants with the following notice concerning the application of pesticides.
CAUTION -- PESTICIDES ARE TOXIC CHEMICALS. Structural Pest Control Operators are licensed and regulated by the Structural
Pest Control Board and apply pesticides which are registered and approved for the use by the California Department of Food and
Agriculture and the United States Environmental Protection Agency. Registration is granted when the state finds that based on
existing scientific evidence, there are no appreciable risks if proper use conditions are followed or that the risks are outweighed by
the benefits. The degree of risk depends upon the degree of exposure, so exposure should be minimized. If rodenticide ingestion
occurs, you may experience symptoms of mild shock and/or bleed anticoagulant reaction. If within 24 hours following application,
you experience flu like symptoms: headaches, dizziness, nausea, tearing, coughing, nose and throat irritation or develop shortness
of breath, double vision, unusual drowsiness and weakness, or tremors, contact your physician, an appropriate licensed health care
provider, or the California Poison Control Center at 1-800-222-1222 and Landlord immediately. For more information, contact your
County Health Department. For regulatory information, contact the Department of Pesticide Regulation at (916) 324-4100.
The following pesticides are commonly used for the extermination of pests. One or more of these materials may be used in your
residential unit. You may request specific information about which pesticides are to be applied and when they are to be applied from
the Property Manager.
• Avert 310 (Abamectin) Whitmire
• Avert Gel (Abamectin) Whitmire
• Advanced Liquid Bait (Boric Acid) Whitmire
• Advanced 375A (Abamectin) Whitmire
• Advanced Gel Bait (Boric Acid) Whitmire
• Borid (Boric Acid) Cline Buckner
• BP 100 or BP 300 (Pyrethrins) Whitmire
• CB-80 Extra (Pyrethins) Waterbury
• Delta Dust (Deltamethrin) Aventis
• Delta Guard (Deltamethrin) Aventis
• Demand SC (Lamba-Cyhalothrin Technical)
Syngents
• Dragnet (Permethirin) FMC
• Drax (Orthoboric Acid) Waterbury
• Drione (Pyrethrins) Agrevo
• Gentrol (Hydroprene) Zoecon
• Maxforce FC Any Gel (Fipronil)
• Maxforce FC Roach Gel (Fipronil)
• Maxforce Granules (Hydramethylnon) Maxforce
• Pestcon Systems Microcare (Pyrethrins)
Whitmire
• Precor (Methoprene) Zoecon
• PT 565 (Pyrethrin) Whitmire
• Perma-Dust PT 240 (Boric Acid) Whitmore
• Pro Control Fogger Plus (Pyrethrins / Cyfluthrin)
Whitmire
• Suspend SC (Deltamethrin) Aventis
• Saga-WP (Tetrabromethyl) Aventis
• Siege (Hydramethylon) Waterbury
• Talstar EZ Granular (Bifenthrin) FMC
• Talstar Liquid (Bifenthrin) FMC
• Tempo Dust (Cyfluthrin) Bayer
• Tempo (Cyfluthrin) Bayer
• Terro Ant Killer II (Boric Acid) Senoret Chem.
• Termidor SC (Fipronil) BASF
• Tri-Die PT 230 (Pyrethrins) Whitmire
• Ultracide Carpet Spray (Permithrin/Nylar)
Whitmire
• Wasp & Hornet Jet Freeze (Pyrethrins)
Waterbury
• Wasp-Freeze PT515 (Tetramethrin / Permethrin
/ Piperonyl Butoxide) Whitmire
WILDLIFE CHEMICALS
• AC 90 (Chlorphacinone) Bell Labs
• Contrac Bait Pck. (Bromadiolone) Bell Labs
• Contrac Blox (Bromadiolone) Bell Labs
• Fumitoxin (Aluminum Phosphide) Pestcon
Systems
• Liquitox (Diphacinone) Bell Labs
• Gopher Getter (Strychnine) Witco
• Mole Patrol (Warfarin) Witco
• Rodent Baits Oats (Chlorphacinone) King
County
• ZP Tracking Powder (Zinc Phosphide) Bell Labs
• ZP (Zinc Phosphide) Bell Labs
2. California law also requires persons exposed to substances regulated under the Safe Drinking and Toxic Enforcement Act of 1986,
commonly referred to as "Proposition 65", to be provided a clear and reasonable warning, as some of the pesticides listed above are
chemicals regulated under Proposition 65. You are advised as follows:
WARNING: The area within your building contains a substance known to the State of California to cause
cancer, birth defects, or other reproductive harm.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 54
3. Resident has read the above disclosure and pesticide list and Resident understands that any of the pesticides listed may have been
used in the past.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 55
FLOOD ZONE DISCLOSURE ADDENDUM
This Flood Zone Disclosure Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the lease agreement
dated 8/25/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of
the Community ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually
and collectively referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz,
CA 95060 ("Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All
terms not specifically defined in this Addendum shall have the same definition as found in the Lease. Landlord and Resident agree
as follows:
1. Pursuant to California Government Code section 8589.45, Resident is hereby notified that the above-referenced Premises and
Community are in a special flood hazard area or an area of potential flooding.
2. Resident hereby acknowledges:
a. Any insurance carried by the Community, including flood insurance, does not cover the loss of Resident’s personal property.
b. It is recommended that Resident purchase flood insurance in addition to renter's insurance to insure Resident’s personal
property from loss due to flood, fire, or other risk of loss.
3. Resident may obtain information about hazards, including flood hazards, that may affect the Community from the California Office
of Emergency Services, available at http://myhazards.caloes.ca.gov/.
4. Resident acknowledges and understands that Landlord and the Community are not required to provide additional information
concerning the flood hazards to the Community and that the information provided in this Addendum is deemed adequate to inform
Resident by Section 8589.45.
5. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective
to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this addendum or
the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of
any conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 56
CALIFORNIA TENANT ACT OF 2019 ADDENDUM
This California Tenant Protection Act of 2019 Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the
lease agreement dated 8/25/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as agent
for Owner of the Community ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai
(individually and collectively referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121,
Santa Cruz, CA 95060 ("Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or
"Property"). All terms not specifically defined in this Addendum shall have the same definition as found in the Lease. Landlord and
Resident agree as follows:
1. In 2019, California enacted the Tenant Protection Act of 2019 (“Act”) implementing statewide rent control and just cause eviction
protections at rental properties subject to the Act. This Addendum relates to the provisions of the Act and remains in force until
the repeal of the Act or the termination of Resident’s tenancy at the Premises, whichever occurs first.
2. Resident hereby acknowledges receipt of the following Notice from Landlord as required by the Tenant Protection Act of 2019:
California law limits the amount your rent can be increased. See Section 1947.12 of the
Civil Code for more information. California law also provides that after all of the tenants
have continuously and lawfully occupied the property for 12 months or more or at least
one of the tenants has continuously and lawfully occupied the property for 24 months or
more, a landlord must provide a statement of cause in any notice to terminate a tenancy.
See Section 1946.2 of the Civil Code for more information.
3. Resident acknowledges that the Act is not applicable to Resident’s household if Resident’s tenancy falls under any Below Market
Rate or Affordable Rental program regulated by the following: rent restriction in a deed, regulatory restriction contained in an
agreement with a government agency, or other recorded document restricting the Unit to affordable housing for person and families
of very low, low, or moderate income, as defined in Section 50093 of the Health and Safety Code, or subject to an agreement that
provides housing subsidies for affordable housing for persons and families of very low, low, or moderate income, as defined in
Section 50093 of the Health and Safety Code or comparable federal statutes. To the extent that Resident’s tenancy falls under any
of the foregoing, Resident acknowledges and understands that the rent control and just cause eviction protections under the Act do
not apply to Resident’s household.
4. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective
to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this addendum or
the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of
any conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 57
SANTA CRUZ SECURITY DEPOSIT ADDENDUM
This Santa Cruz Security Deposit Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the lease agreement
dated 8/25/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of the
Community ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and
collectively referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA
95060 ("Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All terms
not specifically defined in this Addendum shall have the same definition as found in the Lease. Landlord and Resident agree as
follows:
1. Resident is hereby notified by Landlord that the City of Santa Cruz has adopted Sections 21.02.010-21.02.100 of the Santa
Cruz Municipal Code pertaining to the payment of Resident’s Interest on Residential Rental Security Deposit.
2. Resident has the right to receive simple interest from Landlord on Resident's security deposit in accordance with Section 21.02.040
of the Santa Cruz Municipal Code.
3. Resident's security deposit shall bear simple interest at the percentage rate established by City Council resolution for each calendar
year. As of the date of this Addendum, the simple interest rate as set by the Santa Cruz City Council is 1.00%. This interest rate
will change during the tenancy if the City Council changes the required interest rate.
4. Resident shall be entitled to payment of accrued interest at the earlier of the following:
a. Upon termination of tenancy, Resident shall be entitled to a direct payment of the accrued interest then remaining due and
owing no later than twenty-one (21) days after Resident has vacated the Unit; or
b. At the end of the next February occurring after accrued interest reaches fifty dollars ($50.00).
5. If interest is to be paid pursuant to Paragraph 4(b) above, Landlord shall, without demand, pay the accrued interest in the form of
either a draft payment or a credit against Resident's rent. Landlord shall choose between the two methods of payment.
6. Pursuant to Section 21.02.080, upon termination of the tenancy, Resident's accrued interest on any security deposit may be used
by Landlord to supplement Resident's security deposit if, after Landlord complies with California Civil Code section 1950.5, the cost
of verifiable repairs to the Premises exceeds the security deposit. Resident shall be given an accounting of any amount of the
interest on security deposit used by Landlord for repairs of the Unit.
7. Should Landlord fail to disburse interest to Resident or credit Resident's rent, Resident's interest shall, on a daily basis, accrue on
the sum of the principal amount of the security deposit held by Landlord plus the amount of any previous interest earned, but not
disbursed or credited.
8. Landlord also may have potential liability for
a. Statutory damages for failure to comply with any provision of Chapter 21.02 of the Santa Cruz Municipal Code; and
b. Additional liability under California Civil Code Section 1950.5 for the malicious retention of the security deposit
9. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective
to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this addendum or
the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of
any conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 58
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 59
SMOKING POLICY ADDENDUM
This Smoking Policy Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the lease agreement dated 8/25/2025
(the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of the Community
("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai (individually and collectively
referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121, Santa Cruz, CA 95060 ("Premises"
or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All terms not specifically defined
in this Addendum shall have the same definition as found in the Lease. Landlord and Resident agree as follows:
1. The parties desire to mitigate: (i) the irritation and known health effects of secondhand smoke; (ii) the increased maintenance,
cleaning, and redecorating costs from smoking; (iii) the increased risk of fire from smoking; and (iv) the high cost of fire
insurance for properties where smoking is permitted.
2. "Smoking" or “Smoke” means possessing a lighted tobacco product, lighted tobacco paraphernalia, lighted marijuana, or any other
lighted weed or plant (including, but not limited to, a lighted pipe, lighted hookah pipe, lighted cigar, lighted cigarette of any kind),
an electronic smoking device of any kind, or the lighting or emitting or exhaling the smoke or vapor of a tobacco product, tobacco
paraphernalia, marijuana product, or any other weed or plant (including, but not limited to, a pipe, a hookah pipe, cigar, marijuana
product, electronic cigarette or cigarette of any kind). Electronic smoking devices are any battery-operated device that delivers
vapors for inhalation, including every variation and type of such device regardless of how marketed or described.
3. Resident and members of Resident's household shall not Smoke in these designated areas, nor shall Resident permit any guest or
visitor of Resident to do so. Violation of this paragraph by Resident or any other person subject to the control of Resident or
present by invitation or permission of Resident is a material breach of the Lease.
a) Smoking is prohibited in all indoor and outdoor common areas on the property, except for those areas specifically designated
for Smoking, and within twenty-five (25) feet of any entrance, exit, operable windows, vents or other openings into enclosed
non-smoking areas.
b) Residents who Smoke, or allow smoking by their invitees or guests, must ensure the smoke does not disturb the quiet
enjoyment of other residents. Secondhand Smoke may constitute a material breach of the Lease.
4. Resident shall inform their invitees or guests of the provisions contained in this Smoking Policy Addendum and ensure their
compliance with this addendum.
5. Resident acknowledges that Landlord is not a guarantor of the Resident's health or that the areas listed in Paragraph 3 above will
be free of Smoke; however, Landlord shall take reasonable steps to enforce this Addendum. Landlord shall not be required to take
any specific steps in response to Smoking unless Landlord has actual knowledge or has been provided written notice.
6. To the extent provided by applicable law, all lawful occupants of the Apartment Community are express third-party beneficiaries of
this Addendum. If Resident or any Authorized Occupant or Guest breaches this Addendum, or Resident or any Authorized
Occupant knowingly allows Guests to breach this Addendum, Resident potentially will be liable to Landlord and to any resident or
guest of the Apartment Community who is exposed to secondhand smoke because of that breach.
7. Resident acknowledges that this Addendum and Landlord's efforts to designate Non-Smoking Areas do not in any way change the
standard of care that the Landlord would have to any Resident household to render buildings and premises designated as non-
smoking any safer, more habitable, or improved in terms of air quality than any other rental premises. Landlord specifically
disclaims any implied or express warranties that the building common areas or Resident's premises will have any higher or
improved air quality standards than any other rental property. Landlord cannot and does not warrant or promise that the Premises
or any other portion of the Community including common areas will be free from secondhand smoke. Resident acknowledges that
Landlord's ability to police, monitor or enforce this Addendum is dependent in significant part on voluntary compliance by Resident
and Resident's guests.
8. Resident and Landlord agree to comply with all applicable laws relating to smoking at this property. Landlord is not required to
advise Resident of any changes in the law with respect to smoking on the Property. It is a material breach for Resident or any other
person subject to the control of Resident or present by invitation or permission of Resident to violate any law regulating Smoking
while anywhere on the Property To the extent that any provision of this Addendum is in conflict with any provisions of applicable
law, such provision is hereby deleted, and any provision required by applicable law which is not included in this Addendum is
hereby inserted as an additional provision of this Addendum, but only to the extent required by applicable law and then only so
long as the provision of the applicable law is not repealed or held invalid by a court of competent jurisdiction.
9. Landlord may change its smoking policies at any time after providing Resident with thirty (30) days written notice. Thirty (30) days'
notice is not required if a policy change is implemented to comply with a new law or ordinance.
10. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be ineffective
to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this addendum or
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 60
the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain unchanged. In the event of
any conflict between the terms of this Addendum and the terms of the Lease, the terms of this Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: [text|req|signer1||s1u0||name|sn1] Title: Community Manager Date
08 / 05 / 2025
Jay Austin
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 61
OFFER OF POSITIVE RENT REPORTING ADDENDUM
This Offer of Positive Rent Reporting Addendum ("Addendum") dated 07/31/2025 is attached to and made a part of the lease
agreement dated 8/25/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for
Owner of the Property ("Landlord"), and Haardhik Mudagere Anil, Abhishek Chavan, Shubham Sharma, Mathesh Thirumalai,
(individually and collectively referred to herein as "Resident") for the rental of the premises located at 145 Chestnut Street #121
("Premises" or "Unit") within the community commonly known as Chestnut Street (the "Community" or "Property"). All terms not
specifically defined in this Addendum shall have the same definition as found in the Lease.
1. Resident hereby acknowledges receipt of the Written Offer and Election of Positive Rent Reporting pursuant to California Civil
Code 1954.07, attached here as Exhibit A. This provides Resident the option to have the Community provide a record of the
Resident’s positive rent payments (complete, timely payments) to a credit agency on a monthly basis in order to allow the
Resident to build good credit.
2. Resident will be automatically enrolled in the program for their benefit. While Resident will be automatically enrolled even if
Resident takes no action, Resident can also opt-out of positive credit reporting by signing the below form and returning it to
Landlord.
3. If any provision of this Addendum or the Lease is invalid or unenforceable under applicable law, such provision shall be
ineffective to the extent of such invalidity or unenforceability only without invalidating or otherwise affecting the remainder of this
addendum or the Lease. Except as specifically stated herein, all other terms and conditions of the Lease shall remain
unchanged. In the event of any conflict between the terms of this Addendum and the terms of the Lease, the terms of this
Addendum shall control.
RESIDENT:
[sig|req|signer0] [date|req|signer0]
Haardhik Mudagere Anil Date
[sig|req|signer2] [date|req|signer2]
Abhishek Chavan Date
[sig|req|signer3] [date|req|signer3]
Shubham Sharma Date
[sig|req|signer4] [date|req|signer4]
Mathesh Thirumalai Date
LANDLORD:
Essex Management Corporation, a California Corporation, as Agent for Owner
By: [sig|req|signer1] [date|req|signer1]
Print Name: Samantha Pratti Title: Community Manager Date
08 / 05 / 2025
08 / 01 / 2025
07 / 31 / 2025
07 / 31 / 2025
07 / 31 / 2025
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Chestnut Street
Page | 62
EXHIBIT A
WRITTEN OFFER AND ELECTION OF POSITIVE RENT REPORTING
This Written Offer and Election of Positive Rent Reporting (“Offer”) is made to Haardhik Mudagere Anil, Abhishek Chavan, Shubham
Sharma, Mathesh Thirumalai, (individually and collectively referred to herein as "Resident") who signed the lease agreement dated
8/25/2025 (the "Lease") by and between Essex Management Corporation, a California Corporation, as agent for Owner of the Property
("Landlord"), for the rental of the premises located at 145 Chestnut Street #121 ("Premises" or "Unit") within the community commonly
known as Chestnut Street (the "Community" or "Property")
1. Reporting Optional. Reporting of Resident’s positive rent payment history to one or more credit agencies is optional. Landlord will
automatically enroll Resident in Positive Credit Reporting unless Resident elects to opt-out.
2. Opting Out. Resident may opt-out of positive reporting by signing below and notifying Landlord. Upon Resident’s opting out,
Resident may not elect to again have rent reporting for a period of six (6) months after opting out. Resident may not opt-out of
negative credit reporting.
3. Credit Reporting Agency. Landlord shall report positive rent payments to TransUnion (singularly and collectively, the “Agency”)
on a monthly basis.
4. Reporting Fee. Resident shall pay a monthly fee equal to $0.00 while participating in positive rent payment reporting. Resident
understands that if a fee is charged, the failure to pay this amount shall result in the cessation of reporting to the Agency by Landlord
for a period of at least six (6) months, and the unpaid fees cannot be deducted from the security deposit or used as a basis for
eviction. Upon sixty (60) days’ notice, Landlord reserves the right to change the monthly fee for credit reporting. Resident will have
the option to opt-out before the changed fee is imposed.
By signing below, each Resident has elected to opt-out of Positive Credit Reporting and acknowledges that Resident’s
positive rent payments will be reported to the Agency.
RESIDENT:
Haardhik Mudagere Anil Date
Abhishek Chavan Date
Shubham Sharma Date
Mathesh Thirumalai Date
Doc ID: 57f64ebbe5ed011cc492ce97e3c99831f6752e67
Haardhik Mudagere Anil - Chestnut Street (pk=863614) - 25
tmpydskwlke.pdf
57f64ebbe5ed011cc492ce97e3c99831f6752e67
MM / DD / YYYY
Signed
This document was signed on nestiolistings.com
07 / 31 / 2025
18:17:07 UTC
Sent for signature to Haardhik Mudagere Anil
(haardhiknbd@gmail.com), Jay Austin (jaustin@essex.com),
Abhishek Chavan (abchavan@ucsc.edu), Shubham Sharma
(sshar134@ucsc.edu) and Mathesh Thirumalai
(mati02official@gmail.com) from esign@funnelleasing.com
IP: 52.20.204.88
07 / 31 / 2025
18:21:55 UTC
Viewed by Haardhik Mudagere Anil (haardhiknbd@gmail.com)
IP: 128.114.255.219
07 / 31 / 2025
18:27:54 UTC
Viewed by Abhishek Chavan (abchavan@ucsc.edu)
IP: 174.194.130.90
07 / 31 / 2025
18:45:07 UTC
Signed by Haardhik Mudagere Anil (haardhiknbd@gmail.com)
IP: 128.114.255.219
07 / 31 / 2025
19:08:05 UTC
Signed by Abhishek Chavan (abchavan@ucsc.edu)
IP: 128.114.255.253
07 / 31 / 2025
19:21:25 UTC
Viewed by Shubham Sharma (sshar134@ucsc.edu)
IP: 169.233.247.231
08 / 01 / 2025
04:44:37 UTC
Signed by Shubham Sharma (sshar134@ucsc.edu)
IP: 71.198.216.30
08 / 01 / 2025
05:18:02 UTC
Viewed by Mathesh Thirumalai (mati02official@gmail.com)
IP: 68.53.47.234
08 / 01 / 2025
05:19:34 UTC
Signed by Mathesh Thirumalai (mati02official@gmail.com)
IP: 68.53.47.234
Haardhik Mudagere Anil - Chestnut Street (pk=863614) - 25
tmpydskwlke.pdf
57f64ebbe5ed011cc492ce97e3c99831f6752e67
MM / DD / YYYY
Signed
This document was signed on nestiolistings.com
08 / 05 / 2025
21:12:59 UTC
Viewed by Jay Austin (jaustin@essex.com)
IP: 73.92.54.169
08 / 05 / 2025
21:14:14 UTC
Signed by Jay Austin (jaustin@essex.com)
IP: 73.92.54.169
The document has been completed.
08 / 05 / 2025
21:14:14 UTC
Haardhik Mudagere Anil - Chestnut Street (pk=863614) - 25
tmpydskwlke.pdf
57f64ebbe5ed011cc492ce97e3c99831f6752e67
MM / DD / YYYY
Signed
This document was signed on nestiolistings.com
"""

TEST_QUERIES = [
    "What is the monthly rent?",
    "What happens if I pay rent late?",
    "Are pets allowed?",
    "How much is the security deposit?",
    "How do I terminate the lease?",
]


def test_rag_module():
    """Test RAG module directly without HTTP server."""
    print("\n[1] Loading RAG Service...")
    
    try:
        from rag import get_rag_service
        rag_service = get_rag_service()
        print("    ✓ RAG Service loaded")
    except Exception as e:
        print(f"    ✗ Failed to load RAG service: {e}")
        return False

    # Index document
    print("\n[2] Indexing sample lease document...")
    try:
        result = rag_service.index_document(
            text=SAMPLE_LEASE,
            document_id="test_lease",
            use_semantic_chunking=True,
            max_chunk_size=512
        )
        print(f"    ✓ Indexed: {result['num_chunks']} chunks created")
    except Exception as e:
        print(f"    ✗ Indexing failed: {e}")
        return False

    # Test queries
    print("\n[3] Testing queries...")
    print("-" * 60)
    
    for query in TEST_QUERIES:
        print(f"\n📝 Query: \"{query}\"")
        
        try:
            # Get results with scores
            results = rag_service.retrieve_with_scores(
                query=query,
                top_k=2,
                use_reranking=True
            )
            
            # Get formatted context
            context = rag_service.retrieve_context(query=query, top_k=2)
            
            print(f"   Found {len(results)} results:")
            for r in results:
                print(f"   [{r['rank']}] Score: {r['score']:.3f} | "
                      f"BM25: {r['bm25_score']:.2f} | "
                      f"Dense: {r['dense_score']:.2f}")
                # Format text as proper sentences - show full text without truncation
                text = r['text'].strip()
                # Clean up excessive whitespace: normalize multiple spaces/newlines to single space
                text = re.sub(r'\s+', ' ', text)
                # Ensure proper spacing after sentence-ending punctuation
                text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
                # Display full text with proper formatting (no truncation, no ellipsis)
                print(f"       {text}")
            
        except Exception as e:
            print(f"   ✗ Query failed: {e}")

    # Show stats
    print("\n" + "-" * 60)
    print("\n[4] RAG Service Stats:")
    stats = rag_service.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ RAG Module Test Complete!")
    print("=" * 60)
    
    return True


def test_with_server():
    """Test RAG via HTTP endpoints (requires server running)."""
    import requests
    
    BASE_URL = "http://localhost:8000"
    
    print("\n[Testing via HTTP API]")
    print("Make sure server is running: uvicorn app:app --port 8000")
    print("-" * 60)
    
    # Check health
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✓ Server is healthy")
        else:
            print(f"✗ Server returned {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        return False
    
    # Index document
    print("\n[2] Indexing sample lease document...")
    try:
        resp = requests.post(f"{BASE_URL}/rag/index", json={
            "text": SAMPLE_LEASE,
            "document_id": "test_lease",
            "use_semantic_chunking": True,
            "max_chunk_size": 512
        })
        if resp.status_code != 200:
            print(f"    ✗ Indexing failed: {resp.status_code} - {resp.text}")
            return False
        result = resp.json()
        print(f"    ✓ Indexed: {result['num_chunks']} chunks created")
    except Exception as e:
        print(f"    ✗ Indexing failed: {e}")
        return False
    
    # Test queries
    print("\n[3] Testing queries...")
    print("-" * 60)
    
    for query in TEST_QUERIES:
        print(f"\n📝 Query: \"{query}\"")
        
        try:
            # Query via HTTP
            resp = requests.post(f"{BASE_URL}/rag/query", json={
                "query": query,
                "top_k": 2,
                "use_reranking": True
            })
            
            if resp.status_code != 200:
                print(f"   ✗ Query failed: {resp.status_code} - {resp.text}")
                continue
                
            result = resp.json()
            results = result.get('results', [])
            context = result.get('context', '')
            
            print(f"   Found {len(results)} results:")
            for r in results:
                # Get scores (handle cases where they might not be present)
                bm25_score = r.get('bm25_score', 0.0)
                dense_score = r.get('dense_score', 0.0)
                score = r.get('score', 0.0)
                
                print(f"   [{r.get('rank', 0)}] Score: {score:.3f} | "
                      f"BM25: {bm25_score:.2f} | "
                      f"Dense: {dense_score:.2f}")
                
                # Format text as proper sentences - show full text without truncation
                text = r.get('text', '').strip()
                # Clean up excessive whitespace: normalize multiple spaces/newlines to single space
                text = re.sub(r'\s+', ' ', text)
                # Ensure proper spacing after sentence-ending punctuation
                text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
                # Display full text with proper formatting (no truncation, no ellipsis)
                print(f"       {text}")
            
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
    
    # Show stats
    print("\n" + "-" * 60)
    print("\n[4] RAG Service Stats:")
    try:
        resp = requests.get(f"{BASE_URL}/rag/stats")
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"   ✗ Failed to get stats: {resp.status_code}")
    except Exception as e:
        print(f"   ✗ Failed to get stats: {e}")
    
    print("\n" + "=" * 60)
    print("✅ RAG HTTP API Test Complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Test via HTTP (requires server)
        test_with_server()
    else:
        # Test module directly (no server needed)
        test_rag_module()
