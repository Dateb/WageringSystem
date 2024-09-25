use pyo3::prelude::*;
use rayon::prelude::*;
use rand::Rng;
use rand::rngs::SmallRng;
use rand::SeedableRng;

#[pyclass]
#[derive(Clone)]
struct OddsPair {
    #[pyo3(get, set)]
    starting_odds: f32,
    #[pyo3(get, set)]
    offer_odds: f32,
}

#[pymethods]
impl OddsPair {
    /// Define a constructor for OddsPair
    #[new]
    pub fn new(starting_odds: f32, offer_odds: f32) -> Self {
        OddsPair {
            starting_odds,
            offer_odds,
        }
    }
}

fn mc_max_drawdown(
    odds_pairs: &[OddsPair],
    n_bets: u32,
    stake_size: f32,
    rng: &mut SmallRng
) -> f32 {
    let mut wealth: f32 = 0.0;
    let mut peak_wealth: f32 = 0.0;
    let mut max_drawdown: f32 = 0.0;

    let success_probabilities: Vec<f32> = odds_pairs.iter()
        .map(|odds_pair| 1.0 / odds_pair.starting_odds)
        .collect();

    let odds_iter =
        odds_pairs.iter().cycle().zip(success_probabilities.iter().cycle());

    for (odds_pair, success_probability) in odds_iter.take(n_bets as usize) {
        wealth += match rng.gen::<f32>() < *success_probability {
            true => odds_pair.offer_odds - 1.0,
            false => -1.0,
        } * stake_size;

        peak_wealth = peak_wealth.max(wealth);
        max_drawdown = max_drawdown.max(peak_wealth - wealth);
    }

    max_drawdown
}

#[pyfunction]
fn simulate_max_drawdown(
    odds_pairs: Vec<OddsPair>,
    n_bets: u32,
    stake_size: f32,
    n_simulations: usize
) -> PyResult<Vec<f32>> {
    Ok((0..n_simulations)
        .into_par_iter()
        .map(|_| {
            let mut rng = SmallRng::from_entropy();
            mc_max_drawdown(&odds_pairs, n_bets, stake_size, &mut rng)
        })
        .collect())
}

#[pymodule]
fn wagering_utils(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(simulate_max_drawdown, m)?)?;
    m.add_class::<OddsPair>()?;
    Ok(())
}
