"""Deterministic report explanations; works without a language model or new data."""
QUESTIONS = ['What are my rotation options?', 'What does the stress test mean?',
             'What should I check before choosing?', 'Which data and sources were used?']


def answer_report_question(question, report):
    """Read only supplied report fields. No generated forecasts or agronomic claims."""
    q = question.lower()
    if any(term in q for term in ['source', 'nasa', 'data', 'evidence']):
        meta = report.get('data_metadata')
        text = ('**Data in your current report:**\n\n' +
                ('No daily weather has been loaded for this location.' if not meta else
                 f"Daily weather provenance: {meta.get('source', 'NASA POWER live point request')}. "
                 f"Requested coordinates: {meta.get('requested_coordinates', 'See downloaded report metadata')}.") +
                '\n\nThe map uses the supplied regional temperature workbook; its original export metadata is still unconfirmed. '
                'The bundled vegetation example is Ames-only. Soil conditions are farmer inputs; modeled soil wetness, if loaded, is not a field soil test. '
                'Open Full sources and methods below for the source register.')
        return text
    if any(term in q for term in ['stress', 'hot', 'dry', 'drier', 'wetter', 'forecast', 'predict', 'weather', 'rain']):
        settings = report.get('scenario_settings')
        if not settings:
            return '**Stress test:** Load daily weather and select a season with enough valid observations first. No weather forecast has been generated.'
        rows = report.get('scenario_results') or []
        text = (f"**Your weather replay:** {settings['historical_year']}, with "
                f"{settings['temperature_offset_c']:+g}°C added to daily maximum temperature and "
                f"rainfall multiplied by {settings['rainfall_multiplier']:g}. ")
        if rows:
            row = rows[0]
            text += (f"The scenario has {row['Scenario heat days']:g} days at or above 35°C and "
                     f"a longest rainfall gap of {row['Scenario dry run (days)']:g} days inside your entered crop calendar. ")
        return text + ('\n\nAll options use the same growing months, so heat and rainfall-gap counts match. '
                       'The cover assumption only changes which months count as uncovered. This is a what-if test, not a forecast, yield prediction or proof that a rotation saves water.')
    if any(term in q for term in ['check', 'missing', 'uncertain', 'before', 'soil', 'water', 'limit']):
        p = report['farm_inputs']
        return (f"**Before choosing:** Your soil texture is {p['texture'].lower()} and drainage is {p['drainage'].lower()}; "
                f"your water access is {p['water'].lower()}. Confirm these with local information.\n\n"
                'Check planting and harvest dates, actual residue cover, soil moisture, establishment/termination capacity, equipment and a crop outlet. '
                'Living cover uses water. The current report does not calculate soil-health gains, crop yield or water savings.\n\n' +
                '\n'.join(report.get('missing_evidence', [])))
    if any(term in q for term in ['rotation', 'option', 'recommend', 'choose', 'best', 'score', 'priorit']):
        options = report.get('options', [])
        text = '**Options that passed the current catalogue constraints:**\n\n'
        text += '\n\n'.join(f"- **{o['name']}**: {o['sequence']}. Check: {o['risk']}" for o in options)
        excluded = report.get('excluded', [])
        if excluded:
            text += '\n\n**Excluded:** ' + '; '.join(f"{o['option']} — {o['reason']}" for o in excluded)
        return text + '\n\nThe planning index reflects selected priorities, not proven suitability or predicted outcomes. Alternatives currently have reviewed examples only for Iowa corn/soybean systems.'
    return ('I am the **report helper**, not an open-ended AI model. I can explain your rotation options, weather stress test, information gaps and sources. '
            'Choose one of the four question buttons above. For broader questions, connect Ollama on the computer running the app.')
