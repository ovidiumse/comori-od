<script>

export default {
	name: "shared",
	getBaseUrl: function() {
		return process.env.baseUrl;
	},
	getApiUrl: function() {
		return process.client ? process.env.clientApiUrl : process.env.serverApiUrl;
	},
	indexName: process.env.indexName,
	authors: [],
	types: [],
	volumes: [],
	books: [],
	book_imgs: {
		'Meditații la Ev. după Ioan vol. 1': {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_1_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_1_ls.png'
		},
		'Meditații la Ev. după Ioan vol. 2' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_2_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_2_ls.png'
		},
		'Meditații la Ev. după Ioan vol. 3' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_3_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_3_ls.png'
		},
		'Meditații la Ev. după Ioan vol. 4' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_4_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_4_ls.png'
		},
		'Meditații la Ev. după Ioan vol. 5' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_5_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_5_ls.png'
		},
		'Meditații la Ev. după Ioan vol. 6' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_6_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_6_ls.png'
		},
		'Meditații la Ev. după Ioan vol. 7' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_7_sq.png',
			img_ls: '/book_covers/meditatii_ev_ioan/meditatii_ev_ioan_vol_7_ls.png'
		},
		'Istoria unei Jertfe vol. 1' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_1_sq.png',
			img_ls: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_1_ls.png'
		},
		'Istoria unei Jertfe vol. 2' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_2_sq.png',
			img_ls: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_2_ls.png'
		},
		'Istoria unei Jertfe vol. 3' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_3_sq.png',
			img_ls: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_3_ls.png'
		},
		'Istoria unei Jertfe vol. 4' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_4_sq.png',
			img_ls: '/book_covers/istoria_unei_jertfe/istoria_unei_jertfe_vol_4_ls.png'
		},
		'Hristos - Puterea Apostoliei' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/hristos_puterea_apostoliei/hristos_puterea_apostoliei_sq.png',
			img_ls: '/book_covers/hristos_puterea_apostoliei/hristos_puterea_apostoliei_ls.png'
		},
		'Hristos - Marturia mea' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/hristos_marturia_mea/hristos_marturia_mea_sq.png',
			img_ls: '/book_covers/hristos_marturia_mea/hristos_marturia_mea_ls.png'
		},
		'Cântări Nemuritoare vol. 1' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_1_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_1_ls.png'
		},
		'Cântări Nemuritoare vol. 10' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_10_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_10_ls.png'
		},
		'Cântări Nemuritoare vol. 11' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_11_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_11_ls.png'
		},
		'Cântări Nemuritoare vol. 2' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_2_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_2_ls.png'
		},
		'Cântări Nemuritoare vol. 3' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_3_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_3_ls.png'
		},
		'Cântări Nemuritoare vol. 4' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_4_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_4_ls.png'
		},
		'Cântări Nemuritoare vol. 6' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_6_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_6_ls.png'
		},
		'Cântări Nemuritoare vol. 7' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_7_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_7_ls.png'
		},
		'Cântări Nemuritoare vol. 8' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_8_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_8_ls.png'
		},
		'Cântări Nemuritoare vol. 9' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_9_sq.png',
			img_ls: '/book_covers/cantari_nemuritoare/cantari_nemuritoare_vol_9_ls.png'
		},
		'Alergarea Stăruitoare' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/alergarea_staruitoare_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/alergarea_staruitoare_ls.png'
		},
		'Avuţia Sfântului Moştenitor' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/avutia_sfantului_mostenitor_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/avutia_sfantului_mostenitor_ls.png'
		},
		'Calea Bunului Urmaş' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/calea_bunului_urmas_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/calea_bunului_urmas_ls.png'
		},
		'Credinţa Încununată' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/credinta_incununata_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/credinta_incununata_ls.png'
		},
		'Crucea Mântuitoare' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/crucea_mantuitoare_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/crucea_mantuitoare_ls.png'
		},
		'Cununile Slăvite' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/cununile_slavite_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/cununile_slavite_ls.png'
		},
		'Dorim să fim' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/dorim_sa_fim_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/dorim_sa_fim_ls.png'
		},
		'Eterna Iubire' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/eterna_iubire_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/eterna_iubire_ls.png'
		},
		'Garanţia Veşnică' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/garantia_vesnica_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/garantia_vesnica_ls.png'
		},
		'Lumina Iubitului Fiu' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/lumina_iubitului_fiu_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/lumina_iubitului_fiu_ls.png'
		},
		'Lupta cea Bună' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/lupta_cea_buna_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/lupta_cea_buna_ls.png'
		},
		'Mărgăritarul Ascuns' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/margaritarul_ascuns_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/margaritarul_ascuns_ls.png'
		},
		'Mărturisirea Strălucită' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/marturisirea_stralucita_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/marturisirea_stralucita_ls.png'
		},
		'Numele Biruitorului' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/numele_biruitorului_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/numele_biruitorului_ls.png'
		},
		'Piatra Scumpă' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/piatra_scumpa_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/piatra_scumpa_ls.png'
		},
		'Poruncile Iubirii' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/poruncile_iubirii_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/poruncile_iubirii_ls.png'
		},
		'Porţile Veşniciei' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/portile_vesniciei_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/portile_vesniciei_ls.png'
		},
		'Prietenul Tinereţii mele' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/prietenul_tineretii_mele_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/prietenul_tineretii_mele_ls.png'
		},
		'Păşunile Dulci' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/pasunile_dulci_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/pasunile_dulci_ls.png'
		},
		'Răsplata Ascultării' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/rasplata_ascultarii_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/rasplata_ascultarii_ls.png'
		},
		'Semănaţi Cuvântul Sfânt' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/semanati_cuvantul_sfant_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/semanati_cuvantul_sfant_ls.png'
		},
		'Strălucirea Biruinţei' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/stralucirea_biruintei_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/stralucirea_biruintei_ls.png'
		},
		'Săgeţile biruitoare' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/sagetile_biruitoare_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/sagetile_biruitoare_ls.png'
		},
		'Întâi să fim' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/intai_sa_fim_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/intai_sa_fim_ls.png'
		},
		'Şi acum să facem' : {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_ls.png'
		},
		'Tâlcuirea Evangheliilor duminicilor': {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_ls.png'
		},
		'Omilii la Evanghelia după Matei': {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_ls.png'
		},
		'Strângeți Fărâmiturile Vol. 4': {
			author_img: '/td_lg.png',
			img_sq: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_sq.png',
			img_ls: '/book_covers/cugetari_nemuritoare/si_acum_sa_facem_ls.png'
		}
	}
}
</script>