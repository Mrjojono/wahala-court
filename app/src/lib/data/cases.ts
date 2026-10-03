/**
 * WAHALA COURT — 15 dossiers (template GDD §5)
 */

import type { CaseFile } from '$lib/data/model';

export const CASES: ReadonlyArray<CaseFile> = [
	{
		number: 'N°0007',
		accusedName: 'KOFFI',
		charge:
			'Le nommé KOFFI est accusé d’avoir déclaré « j’arrive dans 5 minutes » alors qu’il n’avait même pas quitté son domicile.',
		exhibit: '« Je suis déjà dehors, je tourne juste le coin. »',
		context: 'Délai constaté entre la déclaration et l’arrivée réelle : 47 minutes.',
		category: 'Amitié',
		gravity: 7.5
	},
	{
		number: 'N°0008',
		accusedName: 'MAMADOU K.',
		charge:
			'ACCUSATION : soustraction frauduleuse et préméditée du thiebou dienn du collègue de la compta.',
		exhibit: '« J’ai vu le suspect rôder près du micro-ondes à 11h52 avec une fourchette dans la manche. »',
		context: 'Faits entre 11h45 et 12h05 au réfectoire du 3ème. Tupperware étiqueté vidé.',
		category: 'Travail',
		gravity: 8.5
	},
	{
		number: 'N°0012',
		accusedName: 'AFI',
		charge: 'AFI est accusée d’avoir lu le message WhatsApp et mis « en ligne » sans jamais répondre.',
		exhibit: '« Désolée j’ai pas vu, mon téléphone était en silencieux. »',
		context: 'Bleus confirmés à 21:03. Réponse reçue le lendemain à 14:12.',
		category: 'WhatsApp',
		gravity: 6
	},
	{
		number: 'N°0015',
		accusedName: 'YAO',
		charge: 'YAO est accusé d’avoir « oublié » son portefeuille pile à l’addition.',
		exhibit: '« Je ramène cash demain, c’est sûr. »',
		context: 'Trois repas déjà « remboursés demain ». Solde en souffrance : 18 500 F.',
		category: 'Argent',
		gravity: 7
	},
	{
		number: 'N°0021',
		accusedName: 'SÉNA',
		charge: 'SÉNA est accusée d’avoir cancel un date 12 minutes avant l’heure dite.',
		exhibit: '« En fait je suis fatiguée, on reporte ? »',
		context: 'Le plaignant était déjà devant le resto. Réservation non annulable.',
		category: 'Dating',
		gravity: 8
	},
	{
		number: 'N°0023',
		accusedName: 'KOMLAN',
		charge: 'KOMLAN est accusé d’avoir monopolisé l’AUX pendant tout le trajet zémidjan.',
		exhibit: '« C’est juste une playlist, détends-toi. »',
		context: '42 minutes de Afrobeat à volume max. Conducteur témoin.',
		category: 'Transport',
		gravity: 5.5
	},
	{
		number: 'N°0027',
		accusedName: 'MAMA',
		charge: 'MAMA est accusée d’avoir révélé le crush de sa fille devant toute la famille.',
		exhibit: '« Mais c’est pour rire ! Tout le monde savait déjà. »',
		context: 'Réveillon. Oncle Paul a applaudi. La fille a quitté la table.',
		category: 'Famille',
		gravity: 9
	},
	{
		number: 'N°0033',
		accusedName: 'DJIBRIL',
		charge: 'DJIBRIL est accusé d’avoir « liké » une story de 2019 à 2h du matin.',
		exhibit: '« C’était un accident de pouce, je jure. »',
		context: 'L’algorithme ne ment pas. La plaignante a screenshot.',
		category: 'Dating',
		gravity: 6.5
	},
	{
		number: 'N°0037',
		accusedName: 'FATY',
		charge: 'FATY est accusée d’avoir mangé le dernier beignet promis à tout le bureau.',
		exhibit: '« Il y en avait encore plein tout à l’heure. »',
		context: 'Boîte vide. Miettes sur le clavier. Caméra couloir absente.',
		category: 'Travail',
		gravity: 7
	},
	{
		number: 'N°0042',
		accusedName: 'ISSAM',
		charge: 'ISSAM est accusé d’avoir inventé un embouteillage pour justifier 1h de retard.',
		exhibit: '« Y’avait un accident au rond-point, check Google Maps. »',
		context: 'Google Maps : trafic fluide. Story Instagram à la plage à 10:12.',
		category: 'Transport',
		gravity: 8
	},
	{
		number: 'N°0048',
		accusedName: 'NADIA',
		charge: 'NADIA est accusée d’avoir forwardé le groupe de potes à son nouveau crush.',
		exhibit: '« C’était juste pour qu’il voie le vibe. »',
		context: 'Screenshots du drama interne maintenant chez un inconnu.',
		category: 'WhatsApp',
		gravity: 8.5
	},
	{
		number: 'N°0051',
		accusedName: 'PAMELA',
		charge: 'PAMELA est accusée d’avoir « emprunté » 5 000 F sans prévenir.',
		exhibit: '« Je pensais que c’était OK entre nous. »',
		context: 'Mobile Money à 23:47. Demande d’explication ignorée 3 jours.',
		category: 'Argent',
		gravity: 7.5
	},
	{
		number: 'N°0055',
		accusedName: 'TOBIAS',
		charge: 'TOBIAS est accusé d’avoir spoiler la fin de la série au groupe familial.',
		exhibit: '« Bah de toute façon c’était évident. »',
		context: 'Message envoyé 4 minutes après le générique. Tante Awa en larmes.',
		category: 'Famille',
		gravity: 6
	},
	{
		number: 'N°0059',
		accusedName: 'LÉA',
		charge: 'LÉA est accusée d’avoir ghosté après avoir dit « on se voit bientôt ».',
		exhibit: '« J’étais juste en mode focus, rien de perso. »',
		context: '18 jours de radio silence. Vu sur une story de concert.',
		category: 'Amitié',
		gravity: 7
	},
	{
		number: 'N°0063',
		accusedName: 'MARC',
		charge: 'MARC est accusé d’avoir mis le chauffage à fond puis d’avoir nié.',
		exhibit: '« C’était déjà comme ça quand je suis arrivé. »',
		context: 'Colocataires en short en décembre. Facture EDF +34 %.',
		category: 'Famille',
		gravity: 5
	}
];

export const CASE_OF_THE_DAY: CaseFile = CASES[0];

/** Alias pratique pour les écrans dossier. */
export const dossier = CASE_OF_THE_DAY;
