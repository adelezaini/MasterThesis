#!/bin/bash

for figure in SFisoprene.pdf SFmonoterp.pdf cb_SOA_TOT_relative.pdf N_AER_relative.pdf DOD550_relative.pdf ACTNL_relative.pdf ACTREL_relative.pdf TGCLDLWP.pdf SW_rest.pdf QFLX_EVAP_TOT.pdf FTOT.pdf DIR.pdf NCFT.pdf FREST.pdf barplot_bvoc.pdf SFmonoterp_N_AER_seasons.pdf N_AERvsACTNL.pdf SWTOT.pdf LWTOT.pdf SWDIR.pdf SWCF.pdf LWDIR.pdf LWCF.pdf SW_rest.pdf LW_rest.pdf cb_SOA_TOTvsACTNL.pdf N_AERvsACTREL.pdf cb_SOA_TOTvsACTREL.pdf SW_rest_ALBEDO.pdf ALBEDO_ET_seasons.pdf QFLX_EVAP.pdf QSOIL.pdf
do
    mv $figure main_findings/
done
