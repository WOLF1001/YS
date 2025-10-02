from __future__ import annotations

import sys
from typing import Optional

import click

from .config import load_config
from .kraken_client import KrakenClient
from .legion_client import LegionClient


@click.group()
@click.option("--env-file", type=click.Path(exists=True), default=None, help="Path to .env file")
@click.pass_context
def main(ctx: click.Context, env_file: Optional[str]) -> None:
    cfg = load_config(env_file)
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg


@main.command("balance")
@click.pass_context
def balance(ctx: click.Context) -> None:
    cfg = ctx.obj["config"]
    if not cfg.kraken:
        click.secho("Kraken API keys not configured", fg="red", err=True)
        sys.exit(1)
    client = KrakenClient(cfg.kraken.api_key, cfg.kraken.api_secret)
    data = client.get_balance()
    for asset, amount in sorted(data.items()):
        click.echo(f"{asset}: {amount}")


@main.command("deposit-address")
@click.option("--asset", required=True, help="Asset symbol, e.g., USDT, BTC")
@click.option("--method", required=False, help="Deposit method (network)")
@click.pass_context
def deposit_address(ctx: click.Context, asset: str, method: Optional[str]) -> None:
    cfg = ctx.obj["config"]
    if not cfg.kraken:
        click.secho("Kraken API keys not configured", fg="red", err=True)
        sys.exit(1)
    client = KrakenClient(cfg.kraken.api_key, cfg.kraken.api_secret)
    addrs = client.get_deposit_address(asset=asset, method=method)
    if not addrs:
        click.echo("No addresses returned. Check asset and method.")
        return
    for item in addrs:
        click.echo(f"address: {item.get('address')} | expiretm: {item.get('expiretm')} | tag: {item.get('tag')}")


@main.command("market-order")
@click.option("--pair", required=True, help="Trading pair, e.g., XBTUSDT")
@click.option("--side", required=True, type=click.Choice(["buy", "sell"]))
@click.option("--volume", required=True, help="Order volume as string")
@click.pass_context
def market_order(ctx: click.Context, pair: str, side: str, volume: str) -> None:
    cfg = ctx.obj["config"]
    if not cfg.kraken:
        click.secho("Kraken API keys not configured", fg="red", err=True)
        sys.exit(1)
    client = KrakenClient(cfg.kraken.api_key, cfg.kraken.api_secret)
    result = client.add_order(pair=pair, type_=side, ordertype="market", volume=volume)
    click.echo(result)


if __name__ == "__main__":
    main()
