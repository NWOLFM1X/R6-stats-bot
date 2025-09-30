import requests
import json


with open("jsons/init.json") as f:
    data = json.load(f)
    apiKey = data.get("api-key")


class r6api:
    def __init__(self, API_KEY):
        self.apiHeaders= {
            "X-Api-Key": API_KEY,
            "User-Agent": "R6 Discord Bot"
        }
        # Nuværende sæson NIX PILLE
        self.configUrl = "https://r6.statsapi.net/v1/config"
        self.configRes = requests.get(self.configUrl, headers=self.apiHeaders)
        self.current_season = self.configRes.json()["currentSeason"]

    # Bruges i link commanden til at tjekke om ubisoft accounten er valid!
    def fetch_profile(self, ubi_name: str):
        lookup_url = f"https://r6.statsapi.net/profiles/lookup?displayName={ubi_name}&platform=uplay"
        lookup_res = requests.get(url=lookup_url, headers=self.apiHeaders)
        lookup_data = lookup_res.json()
        profile_id = lookup_data.get("profileId")
        if not profile_id:
            print(f"⚠️ Ingen profil med navnet {ubi_name}")
            return None
        else:
            return profile_id

    # Funktionen der henter folks rank fra api'en
    def fetch_rank(self, ubi_name: str):
        lookup_url = f"https://r6.statsapi.net/profiles/lookup?displayName={ubi_name}&platform=uplay"
        lookup_res = requests.get(lookup_url, headers=self.apiHeaders)

        if lookup_res.status_code != 200:
            raise Exception(f"Couldn't fetch rank for {ubi_name}. Status code: {lookup_res.status_code}")

        lookup_data = lookup_res.json()
        profileId = lookup_data.get("profileId")
        if not profileId:
            print(f"Ingen profil fundet med navnet {ubi_name}")
            return None

        profile_url = f"https://r6.statsapi.net/profiles/{profileId}"
        profile_res = requests.get(profile_url, headers=self.apiHeaders)

        if profile_res.status_code != 200:
            print(f"❌ Stats.cc: Profilfejl for {ubi_name} (status: {profile_res.status_code})")
            return None

        data = profile_res.json()
        seasonal = data.get("seasonalRecords", {})
        if not seasonal:
            print(f"ingen sæson data for {ubi_name}")
            return None

        if self.current_season in seasonal:
            rankedData = seasonal[self.current_season].get("ranked")
            if rankedData and rankedData.get("maxRank"):
                rank = rankedData.get("maxRank")
                #print(f"{ubi_name} er i rank: {rank}")
                return rank
        else:
            print(f"{ubi_name} har ikke nogen rank!")
            return "Copper"

    # Henter kills og deaths fra api og omregner til kd
    def kdRatio(self, ubi_name: str):
        lookup_url = f"https://r6.statsapi.net/profiles/lookup?displayName={ubi_name}&platform=uplay"
        lookup_res = requests.get(lookup_url, headers=self.apiHeaders)

        lookup_data = lookup_res.json()

        # hent nyeste sæson direkte fra API'en
        config_url = f"https://r6.statsapi.net/v1/config"
        config_res = requests.get(url=config_url, headers=self.apiHeaders)
        current_season = config_res.json()["currentSeason"]

        profile_id = lookup_data.get("profileId")

        profile_url = f"https://r6.statsapi.net/profiles/{profile_id}"
        profile_res = requests.get(profile_url, headers=self.apiHeaders)

        data = profile_res.json()
        seasonal = data.get("seasonalRecords", {})

        if current_season in seasonal:
            ranked_data = seasonal[current_season].get("ranked")
            kills = ranked_data["kills"]
            deaths = ranked_data["deaths"]
            if kills is not None and deaths > 0:
                kd_ratio = round(kills / deaths, 2)
                return round(kd_ratio, 2)