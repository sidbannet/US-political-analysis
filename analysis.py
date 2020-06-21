## US election analysis
(
    np.array(
        df_election_pres[
            df_election_pres.FIPS == 1001
        ][
            df_election_pres.party == 'republican'
        ].candidatevotes
    ) / np.array(
        df_election_pres[
            df_election_pres.FIPS == 1001
        ][
            df_election_pres.party == 'republican'
        ].totalvotes
    )
).mean() * 100.00
