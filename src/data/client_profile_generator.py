"""Generator for 50,000 realistic client profiles across risk categories."""

from typing import List, Optional
import numpy as np

from src.core.constants import Country, ESGPreference, RiskCategoryKey, TaxBracket
from src.core.logger import get_logger
from src.core.utils import Timer
from src.models.client import ClientProfile
from src.models.security import Security

logger = get_logger(__name__)

FIRST_NAMES = [
    "Aarav", "Aditi", "Arjun", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Rahul", "Kavya",
    "Dev", "Isha", "Siddharth", "Meera", "Kabir", "Riya", "Aditya", "Pooja", "Varun", "Shreya",
    "James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Benjamin", "Isabella",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Mehta", "Gupta", "Singh", "Reddy", "Nair", "Joshi", "Rao",
    "Kapoor", "Chopra", "Deshmukh", "Iyer", "Kumar", "Smith", "Johnson", "Williams", "Brown", "Jones",
]


class ClientProfileGenerator:
    """Enterprise generator producing 50,000 realistic client profiles."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    def generate_clients(
        self,
        num_clients: int = 50000,
        securities: Optional[List[Security]] = None,
    ) -> List[ClientProfile]:
        """Generate client profiles matching robo-advisory demographic specifications.

        Args:
            num_clients: Total clients to generate (default: 50,000).
            securities: Optional list of securities to sample restricted tickers from.

        Returns:
            List of validated ClientProfile objects.
        """
        with Timer(f"Generating Client Profiles ({num_clients} clients)"):
            clients: List[ClientProfile] = []

            # Risk Category distribution:
            # Ultra Conservative (10%), Conservative (20%), Balanced (40%), Aggressive (20%), Ultra Aggressive (10%)
            risk_keys = [
                RiskCategoryKey.ULTRA_CONSERVATIVE,
                RiskCategoryKey.CONSERVATIVE,
                RiskCategoryKey.BALANCED,
                RiskCategoryKey.AGGRESSIVE,
                RiskCategoryKey.ULTRA_AGGRESSIVE,
            ]
            risk_probs = [0.10, 0.20, 0.40, 0.20, 0.10]
            assigned_risks = self.rng.choice(risk_keys, size=num_clients, p=risk_probs)

            # Tax Brackets & ESG preferences
            tax_brackets = list(TaxBracket)
            esg_prefs = list(ESGPreference)
            countries = list(Country)
            country_probs = [0.70, 0.10, 0.05, 0.05, 0.05, 0.05]

            # Vectorized sampling for wealth distribution
            # Annual income lognormal mean ~ 1,500,000 INR
            incomes = self.rng.lognormal(mean=14.2, sigma=0.8, size=num_clients)
            incomes = np.clip(incomes, 300000.0, 50000000.0)

            # Portfolio sizes correlated with income + lognormal noise
            portfolio_sizes = incomes * self.rng.lognormal(mean=1.2, sigma=0.5, size=num_clients)
            portfolio_sizes = np.clip(portfolio_sizes, 50000.0, 250000000.0)

            # Investment horizons (1-30 years)
            horizons = self.rng.randint(1, 31, size=num_clients)

            # Available security tickers for restriction assignment
            ticker_pool = [s.ticker for s in securities] if securities else []

            # Pre-generate names randomly
            fn_indices = self.rng.randint(0, len(FIRST_NAMES), size=num_clients)
            ln_indices = self.rng.randint(0, len(LAST_NAMES), size=num_clients)

            for i in range(num_clients):
                client_id = f"CLT_{i + 1:05d}"
                name = f"{FIRST_NAMES[fn_indices[i]]} {LAST_NAMES[ln_indices[i]]}"
                risk_cat = assigned_risks[i]

                # Tax bracket correlated with income
                inc = incomes[i]
                if inc < 500000:
                    tb = TaxBracket.SLAB_0
                elif inc < 1000000:
                    tb = TaxBracket.SLAB_10
                elif inc < 2000000:
                    tb = TaxBracket.SLAB_20
                elif inc < 5000000:
                    tb = TaxBracket.SLAB_30
                else:
                    tb = TaxBracket.SLAB_35

                esg = esg_prefs[self.rng.randint(0, len(esg_prefs))]
                cntry = countries[self.rng.choice(len(countries), p=country_probs)]

                # Random restricted securities (10% chance of having restrictions)
                restricted: List[str] = []
                if ticker_pool and self.rng.rand() < 0.10:
                    num_restr = self.rng.randint(1, 4)
                    restricted = list(self.rng.choice(ticker_pool, size=num_restr, replace=False))

                # Upcoming cash flow (15% chance of upcoming cash flow event)
                cash_flow = 0.0
                if self.rng.rand() < 0.15:
                    # Deposit (+) or withdrawal (-)
                    direction = 1.0 if self.rng.rand() > 0.3 else -1.0
                    cash_flow = round(direction * float(portfolio_sizes[i]) * self.rng.uniform(0.02, 0.10), 2)

                cp = ClientProfile(
                    client_id=client_id,
                    name=name,
                    risk_category=risk_cat,
                    tax_bracket=tb,
                    investment_horizon=int(horizons[i]),
                    annual_income=round(float(inc), 2),
                    portfolio_size=round(float(portfolio_sizes[i]), 2),
                    esg_preference=esg,
                    restricted_securities=restricted,
                    upcoming_cash_flow=cash_flow,
                    country=cntry,
                )
                clients.append(cp)

            logger.info(f"Successfully generated {len(clients)} client profiles.")
            return clients
